from datetime import datetime
from time import sleep
from typing import List
from tcp_server import Tcp_Server
from tcp_logger_server_info import Tcp_Logger_Server_Info
from file_logger import File_Logger
from time_graph import Event, Message, Time_Graph
from threading import Thread

first_time = 0
run = True
messages : List[Message] = []

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

# [2021-09-01 23:50:13.446] - [server] - [2021-09-01 23:50:13.445] - [F3] - [RAFT_SM] - FOLLOWER
def parser(data):
    fields = data.split(' - ')
    ms = get_ms(fields[0])
    node_origin = fields[1][1:-1]
    cmd = fields[2][1:-1]

    if not time_graph.has_node(node_origin):
        time_graph.insert_node(node_origin)
    
    if cmd == 'RAFT_SM': # FOLLOWER|CANDIDATE|LEADER
        state = fields[3]
        node = time_graph.get_node(node_origin)
        last_event : Event = node.get_last_event()
        
        if last_event and last_event.type.name == state:
            node.update_event(last_event, int(ms))
        else:
            event_time = int(ms)
            if not last_event:
                event_time = 0
            node.insert_event(Event(int(event_time), 0, state))

    elif cmd == 'SEND': # request_vote;F3;1;F1
        fields_data = fields[3].split(';')
        type = fields_data[0]
        node_origin = time_graph.get_node(fields_data[1])
        
        if not time_graph.has_node(fields_data[3]):
            time_graph.insert_node(fields_data[3])
        
        node_destiny = time_graph.get_node(fields_data[3])
        
        found_message = False
        for idx, message in enumerate(messages):
            if message.type == type and message.origin.name == node_origin.name and message.destiny.name == node_destiny.name:
                message.send_time = ms
                time_graph.insert_message(message)
                found_message = True
                messages.pop(idx)
                break
        
        if not found_message:
            message = Message(node_origin, node_destiny, type, ms, -1)
            messages.append(message)
    
    elif cmd == 'RECEIVED': # request_vote;F3;1;F1
        fields_data = fields[3].split(';')
        type = fields_data[0]
        node_destiny = time_graph.get_node(fields_data[3])
        
        if not time_graph.has_node(fields_data[1]):
            time_graph.insert_node(fields_data[1])
        
        node_origin = time_graph.get_node(fields_data[1])
        
        found_message = False
        for idx, message in enumerate(messages):
            if message.type == type and message.origin.name == node_origin.name and message.destiny.name == node_destiny.name:
                message.receive_time = ms
                time_graph.insert_message(message)
                found_message = True
                messages.pop(idx)
                break
        
        if not found_message:
            message = Message(node_origin, node_destiny, type, -1, ms)
            messages.append(message)

def on_receive(self, log):
    log_str = log.decode("utf-8")
    
    parser(log_str)
    file_logger.save(log_str)

def thread_check_keyboard():
    global run

    while True:
        answer = input("<s:stop>: ") ## blocking read
        if answer == "s":
            run = False
            break

if __name__ == "__main__":

    file_logger = File_Logger('server', False)
    tcp_logger_server_info = Tcp_Logger_Server_Info()
    tcp_server = Tcp_Server(tcp_logger_server_info.port, on_receive)
    time_graph = Time_Graph()
    
    Thread(target = thread_check_keyboard).start()

    while True:
        if run:
            time_graph.plot()
        else:
            time_graph.plot_end()
            break

        sleep(1)