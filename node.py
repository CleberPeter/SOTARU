import sys
import os
import json
import crypto
from time import sleep
from raft import Raft
from http_server import HttpServer


class Node:

    def __init__(self, name, tcp_server_port, http_server_port, force_leader = False):

        print("NODE_" + name + ": init")
        self.name = name
        self.tcp_server_port = tcp_server_port
        self.http_server_port = http_server_port
        self.raft = Raft(self.name, tcp_server_port, force_leader)
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

        self.raft.suspend()
        sleep(int(time))
        self.raft.resume()

    # TODO: implement unidirectional failures

    def add_author(self, author_data_json, answer):

        print("NODE_" + name + ": add_author")

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

    name = sys.argv[1]
    tcp_server_port = int(sys.argv[2])
    http_server_port = int(sys.argv[3])

    force_leader = False
    if len(sys.argv) > 4:
        if sys.argv[4] == 'force_leader':
            force_leader = True

    node = Node(name, tcp_server_port, http_server_port, force_leader)
