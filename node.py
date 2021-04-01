from time import sleep
from raft import Raft
import sys

class Node:
    def __init__(self, name, sever_port):
        print('NODE_' + name + ': init')
        self.name = name
        self.raft = Raft(self.name, sever_port)
        
if __name__ == "__main__":

    name = sys.argv[1]
    sever_port = int(sys.argv[2])
    node = Node(name, sever_port)