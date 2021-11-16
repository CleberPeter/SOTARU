from time import sleep
from tcp_logger import Tcp_Logger
from network import ClientNode, ManufacturerNode, Network
from helper import Helper
from tcp_client import Tcp_Client
from raft import Message
from threading import Thread


class Client:
    def __init__(self, internal_ip, external_ip, network : Network):
        self.node : ClientNode = network.get_client_node_info(internal_ip, external_ip)
        self.tcp_logger = Tcp_Logger(self.node.name)

        start_msg = '[INITIALIZED] - ' + self.node.get_str_info()
        self.tcp_logger.save(start_msg)

        Thread(target = self.process_client, args=()).start()

    def process_client(self):
        
        sleep(7)
        try:
            msg = Message('append_entries', self.node.name, 0, self.node.father_node.name, 0, 0, 'aui', 0)
            socket = Tcp_Client(self.node.father_node.host, self.node.father_node.tcp_port, self.client_on_receive)
            self.send(socket, msg)

        except Exception as e:  # fail to connect
            self.log_fail_to_connect(self.node, e)

    def send(self, socket, msg : Message):
        msg_str = msg.to_csv()
        self.tcp_logger.save('[SEND] - ' + msg_str)

        socket.send(msg_str)

    def client_on_receive(self, server, data):
        data_str = data.decode("utf-8")
        self.tcp_logger.save('[RECEIVED] - ' + data_str)
        server.close()

    def log_fail_to_connect(self, node_destiny : ManufacturerNode, e : Exception):
        self.tcp_logger.save('[FAIL_CONNECT] - ' + node_destiny.name + ';' + str(e))

if __name__ == "__main__":
    while(True):
        try:
            internal_ip = Helper.get_internal_ip()
            external_ip = Helper.get_external_ip()
            break
        except:
            sleep(1)
    
    network = Network('network_info.csv')
    Client(internal_ip, external_ip, network)