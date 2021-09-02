from datetime import datetime
from time import sleep
from tcp_server import Tcp_Server
from tcp_logger_server_info import Tcp_Logger_Server_Info
from file_logger import File_Logger
from time_graph import Event, Time_Graph

first_time = 0
enabled_receive = True

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

    if cmd == 'RAFT_SM':
        state = fields[3]
        node = time_graph.get_node(node_origin)
        last_event : Event = node.get_last_event()
        
        if not last_event or last_event.type.name != state:
            if last_event:
                node.insert_event(Event(int(ms), 0, state))
            else:
                node.insert_event(Event(0, 0, state))
        else:
            node.update_event(last_event, int(ms))

def on_receive(self, log):
    if enabled_receive:
        log_str = log.decode("utf-8")
        
        parser(log_str)
        file_logger.save(log_str)

if __name__ == "__main__":
    
#    parser('[2021-09-02 01:46:55.160] - [F3] - [RAFT_SM] - FOLLOWER')
#    parser('[2021-09-02 01:46:56.258] - [F3] - [RAFT_SM] - CANDIDATE')
    file_logger = File_Logger('server', False)
    tcp_logger_server_info = Tcp_Logger_Server_Info()
    tcp_server = Tcp_Server(tcp_logger_server_info.port, on_receive)
    time_graph = Time_Graph()

    sleep(10)
    enabled_receive = False

    nodes = time_graph.nodes
    """
    for node in nodes:
        print(' ')
        print('node:',node.name)
        for event in node.events:
            print('type:', event.type.name)
            print('init:', event.init)
            print('size:', event.size)"""

    time_graph.plot()