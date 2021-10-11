import subprocess
from datetime import datetime
from time import sleep
from typing import List
from tcp_server import Tcp_Server
from tcp_logger_server_info import Tcp_Logger_Server_Info
from file_logger import File_Logger
from time_graph import Event, Message, Message_Types, Raft_States, Time_Graph
from threading import Thread

first_time = 0
run = True
messages : List[Message] = []
core_process = []
time_graph = []
restarting = False

# [2021-09-01 23:50:13.446] -> 446
def get_ms(event_time):
    global first_time

    event_time = event_time[1:-1]
    event_time = datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S.%f")
    if first_time:
        diff_time = event_time - first_time        
        return diff_time.seconds*1e3 + diff_time.microseconds / 1e3
    else:
        first_time = event_time
        return 0

def get_message_index(id):
    for idx, message in enumerate(messages):
        if message.id == id:
            return idx
    return -1

# [2021-09-01 23:50:13.446] - [server] - [2021-09-01 23:50:13.445] - [F3] - [RAFT_SM] - FOLLOWER
def parser(data):
    global restarting

    fields = data.split(' - ')
    ms = get_ms(fields[0])
    node_origin = fields[1][1:-1]
    cmd = fields[2][1:-1]
    
    if cmd == 'INITIALIZED': # name: F2, host: 10.0.0.3, external_ip: 172.16.0.4, tcp_port: 5555, http_port: 8080
        fields_data = fields[3].split(',')
        external_ip_fields = fields_data[2].split(':')
        external_ip = external_ip_fields[1][1:]
        
        time_graph.create_node(node_origin, external_ip)

    elif cmd == 'KILL' or cmd == 'RESET' or cmd == 'SUSPEND':
        node = time_graph.get_node(node_origin)
        event_time = int(ms)
        node.insert_event(Event(int(event_time), 0, Raft_States.OFFLINE))

    elif cmd == 'RAFT_SM': # FOLLOWER|CANDIDATE|LEADER
        raft_state = fields[3]
        node = time_graph.get_node(node_origin)
        last_event : Event = node.get_last_event()
                
        if last_event and last_event.raft_state.name == raft_state:
            node.update_event(last_event, int(ms))
        else:
            event_time = int(ms)
            #if not last_event:
                #event_time = 0
            node.insert_event(Event(int(event_time), 0, Raft_States[raft_state]))
        
        # if raft_state == 'LEADER' and not restarting:
            # this thread don't freeze tcp server and allow
            # receive the latest messages from core
            # restarting = True
            # Thread(target = restart).start() 

    elif cmd == 'FAIL_CONNECT': # $destiny_name;$msg
        fields_data = fields[3].split(';')
        
        type = Message_Types.fail_connect
        node_origin = time_graph.get_node(node_origin)
        node_destiny = time_graph.get_node(fields_data[0])
        
        message = Message(0, node_origin, node_destiny, type, ms, ms+1)
        time_graph.insert_message(message)

    elif cmd == 'SEND' or cmd == 'RECEIVED': # $type;$origin_name;$term;$destiny_name;$prev_index;$prev_term;$data;$data_term
        fields_data = fields[3].split(';')
        
        id = int(fields_data[0])
        type = Message_Types[fields_data[1]]
        node_origin = time_graph.get_node(fields_data[2])
        node_destiny = time_graph.get_node(fields_data[4])
        
        msg_index = get_message_index(id)
        if msg_index != -1:
            message = messages[msg_index]

            if cmd == 'SEND':
                message.send_time = ms
            elif cmd == 'RECEIVED':
                message.receive_time = ms
            
            time_graph.insert_message(message)
            messages.pop(msg_index)
        else:
            if cmd == 'SEND':
                message = Message(id, node_origin, node_destiny, type, ms, -1)
            elif cmd == 'RECEIVED':
                message = Message(id, node_origin, node_destiny, type, -1, ms)
            
            messages.append(message)
    
def on_receive(self, log):
    log_str = log.decode("utf-8")
    
    file_logger.save(log_str)
    parser(log_str)

def thread_check_keyboard():
    global run

    while True:
        answer = input("<s:stop|l:limits|k:kill_core>: ") ## blocking read
        if answer == "s":
            run = False
        elif answer == "l":
            if not run:
                limits_srt = input("<inf_sup>: ")
                limits = limits_srt.split('_')
                time_graph.plot_update_limits(int(limits[0]),int(limits[1]))
            else:
                print('stop first.')
        elif answer == "k":
            end_core()
        else:
            print('command not recognitzed.')

def restart():
    global restarting, first_time 

    print('restarting')
    end_core()

    sleep(5)
    first_time = 0
    time_graph.clear()
    start_core()
    
    restarting = False

def end_core():
    global core_process    
    core_process.communicate(b'end')
    
def start_core():
    global core_process
    core_process = subprocess.Popen(["core-python", "deploy_network.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

if __name__ == "__main__":

    file_logger = File_Logger('server', False)
    tcp_logger_server_info = Tcp_Logger_Server_Info()
    tcp_server = Tcp_Server(tcp_logger_server_info.port, on_receive)
    
    Thread(target = thread_check_keyboard).start()

    time_graph = Time_Graph()
    start_core()
    
    time_graph.plot_init()
    while True:
        if run:
            time_graph.plot()
        else:
            time_graph.plot_end()
            break

        sleep(1)