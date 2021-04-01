from node import Node
import nodes_info as nodes_info
from http.server import BaseHTTPRequestHandler, HTTPServer

class Network:

    def __init__(self):
        print('NETWORK: init')

    def start(self):

        nodes = nodes_info.get()

        #for node in nodes:
        #    Node(node.name, node.port)

if __name__ == "__main__":

    network = Network()
    network.start()
