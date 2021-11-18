import os
import json
import crypto

from time import sleep
from helper import Helper
from network import ManufacturerNode, Network
from tcp_logger import Tcp_Logger
from file_logger import File_Logger
from raft import Raft
from http_server import HttpServer

class Node:

    def __init__(self, internal_ip, external_ip, network : Network, force_leader = False):
        self.node : ManufacturerNode = network.get_manufacturer_node_info(internal_ip, external_ip)
        self.tcp_logger = Tcp_Logger(self.node.name)

        if self.node.name == 'F7':
            force_leader = True
            
        self.raft = Raft(self.node.name, network, self.node.tcp_port, self.tcp_logger, force_leader)
        self.http_sever = HttpServer(self.node.http_port, self.on_http_server_receive)

        start_msg = '[INITIALIZED] - ' + self.node.get_str_info()
        self.tcp_logger.save(start_msg)
    
    def kill(self):
        self.tcp_logger.save("[KILL]")

        pid = str(os.getpid())
        cmd = "kill " + pid

        os.system(cmd)

    def reset(self, time):
        self.tcp_logger.save("[RESET]")

        pid = str(os.getpid())
        cmd = "kill " + pid
        cmd += "; sleep " + time + ";"
        cmd += "python3 node.py"
        
        os.system(cmd)

    def suspend(self, time):
        self.tcp_logger.save("[SUSPEND]")

        self.raft.suspend()
        sleep(int(time))
        self.raft.resume()

    def start(self):
        self.raft.start()

    # TODO: implement unidirectional failures
    def add_author(self, author_data_json, answer):

        self.tcp_logger("[ADD_AUTHOR]")

        author_data = json.loads(author_data_json)
        (sk, pk) = crypto.ecdsa_gen_pair_keys()

        answer['private_key'] = sk
        author_data['public_key'] = pk

        return self.raft.publish('add_author', author_data)

    def on_http_server_receive(self, keys, values):

        answer = {}
        status = True
        if keys[0] == "action":
            if values[0] == "start":
                self.start()
            elif values[0] == "kill":
                self.kill()
            elif values[0] == "reset":
                time = values[1]
                self.reset(time)
            elif values[0] == "suspend":
                time = values[1]
                self.suspend(time)
            elif values[0] == "add_author":
                author_data_json = values[1]
                (status, msg) = self.add_author(author_data_json, answer)
        else:
            status = False
            msg = 'action not recognitzed.'

        if status:
            answer['status'] = "success"
        else:
            answer = {}  # clean answer
            answer['status'] = "error"
            answer['msg'] = msg

        return json.dumps(answer)

if __name__ == "__main__":
    while(True):
        try:
            internal_ip = Helper.get_internal_ip()
            external_ip = Helper.get_external_ip()
            break
        except:
            sleep(1)
    
    network = Network('network_info.csv')
    Node(internal_ip, external_ip, network, force_leader = False)
    