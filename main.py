import network
import os
from threading import Thread


def init_node_process(node):
    cmd = "python3 node.py " + node.name + " " + \
        str(node.tcp_port) + " " + str(node.http_port)

    if node.name == "A":
        cmd += " force_leader"

    os.system(cmd)


if __name__ == "__main__":

    nodes = network.get_info()

    for node in nodes:
        thread = Thread(target=init_node_process, args=([node, ]))
        thread.start()
