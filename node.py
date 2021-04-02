import sys
import os
from raft import Raft
from http_server import HttpServer


class Node:

    def __init__(self, name, tcp_server_port, http_server_port):

        print('NODE_' + name + ': init')
        self.name = name
        self.raft = Raft(self.name, tcp_server_port)
        self.http_sever = HttpServer(http_server_port, self.on_http_server_receive)

    def kill(self):

        print('NODE_' + name + ': killed')

        pid = os.getpid()
        cmd = "kill " + str(pid)
        os.system(cmd)

    def on_http_server_receive(self, keys, values):

        for key,value in zip(keys, values):
            if key == 'action':
                if value == 'kill':
                    self.kill()


if __name__ == "__main__":

    name = sys.argv[1]
    tcp_server_port = int(sys.argv[2])
    http_server_port = int(sys.argv[3])
    node = Node(name, tcp_server_port, http_server_port)
