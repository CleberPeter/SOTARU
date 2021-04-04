import sys
import os
import json
import crypto
from time import sleep
from raft import Raft
from http_server import HttpServer


class Node:

    def __init__(self, name, tcp_server_port, http_server_port):

        print("NODE_" + name + ": init")
        self.name = name
        self.tcp_server_port = tcp_server_port
        self.http_server_port = http_server_port
        self.raft = Raft(self.name, tcp_server_port)
        self.http_sever = HttpServer(
            http_server_port, self.on_http_server_receive)

    def kill(self):

        print("NODE_" + self.name + ": killed")

        pid = str(os.getpid())
        cmd = "kill " + pid
        os.system(cmd)

    def reset(self, time):

        print("NODE_" + name + ": reset")

        pid = str(os.getpid())
        cmd = "kill " + pid
        cmd += "; sleep " + time + ";"
        cmd += "python3 node.py " + self.name + " " + \
            str(self.tcp_server_port) + " " + str(self.http_server_port)

        os.system(cmd)

    def suspend(self, time):

        print("NODE_" + name + ": suspend")

        pid = str(os.getpid())
        cmd = "kill -STOP " + pid
        cmd += "; sleep " + time + ";"
        cmd += "kill -CONT " + pid

        os.system(cmd)

    def add_author(self, author_data_json, answer):

        print("NODE_" + name + ": add_author")

        author_data = json.loads(author_data_json)

        (sk, pk) = crypto.ecdsa_gen_pair_keys()

        answer['private_key'] = sk

        print(pk)
        
        return True

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
                status = self.add_author(author_data_json, answer)

        if status:
            answer['status'] = "success"
        else:
            answer['status'] = "error"

        return json.dumps(answer)


if __name__ == "__main__":

    name = sys.argv[1]
    tcp_server_port = int(sys.argv[2])
    http_server_port = int(sys.argv[3])
    node = Node(name, tcp_server_port, http_server_port)
