from node import Node
import nodes_info as nodes_info
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from threading import Thread


class Network:

    def __init__(self):
        print('NETWORK: init')

    def start(self):
        nodes = nodes_info.get()

        for node in nodes:
            self.thread = Thread(target=self.init_node_process, args=([node, ]))
            self.thread.start()

    def init_node_process(self, node):
        cmd = "python3 node.py " + node.name + " " + str(node.port)
        os.system(cmd)

if __name__ == "__main__":

    network = Network()
    network.start()
