import os
import json
import crypto

from time import sleep
from helper import Helper
from network import Network, NodeInfo
from tcp_logger import Tcp_Logger
from file_logger import File_Logger
from raft import Raft
from http_server import HttpServer

class Node:

    def __init__(self, node_info : NodeInfo, force_leader = False):

        self.node_info = node_info
        tcp_logger = Tcp_Logger(node.name)
        self.raft = Raft(self.node_info.name, self.node_info.tcp_port, tcp_logger, force_leader)
        # self.http_sever = HttpServer(self.node_info.http_port, self.on_http_server_receive)

        start_msg = '[INITIALIZED] - ' + node.get_str_info()
        tcp_logger.save(start_msg)
    
    def kill(self):

        print("NODE_" + self.name + ": killed")

        pid = str(os.getpid())
        cmd = "kill " + pid
        os.system(cmd)

    def reset(self, time):
        
        print("NODE_" + self.name + ": reset")

        pid = str(os.getpid())
        cmd = "kill " + pid
        cmd += "; sleep " + time + ";"
        cmd += "python3 node.py " + self.name + " " + \
            str(self.tcp_server_port) + " " + str(self.http_server_port)

        os.system(cmd)

    def suspend(self, time):
        
        self.raft.suspend()
        sleep(int(time))
        self.raft.resume()

    # TODO: implement unidirectional failures
    def add_author(self, author_data_json, answer):

        print("NODE_" + self.name + ": add_author")
        author_data = json.loads(author_data_json)
        (sk, pk) = crypto.ecdsa_gen_pair_keys()

        answer['private_key'] = sk
        author_data['public_key'] = pk

        return self.raft.publish('add_author', author_data)

    def on_http_server_receive(self, keys, values):

        answer = {}
        status = True
        if keys[0] == "action":
            if values[0] == "kill":
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

    my_ip = Helper.get_ip()
    node : NodeInfo = Network.get_node_info(my_ip)
    
    if node:
        Node(node, force_leader = False)
    else:
        file_logger = File_Logger('none')
        error_msg = "can't find node_ip [" + my_ip + "] on network list."
        file_logger.save(error_msg)
        
        exit(-1)