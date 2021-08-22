from typing import List


class NodeInfo:
    def __init__(self, name, host, tcp_port, http_port):
        self.name = name
        self.host = host
        self.tcp_port = tcp_port
        self.http_port = http_port
    
    def get_str_info(self):
        ret = 'name: ' + self.name + ', '
        ret += 'host: ' + self.host + ', '
        ret += 'tcp_port: ' + str(self.tcp_port) + ', '
        ret += 'http_port: ' + str(self.http_port)
        return ret

class Network:
    def get_nodes() -> List[NodeInfo]:
        nodes : NodeInfo = []
        with open('network_info.csv') as file:
            for line in file:
                if line[0] != '#': # jump comments
                    (name, host, tcp_port, http_port) = line.split(',')
                    nodes.append(NodeInfo(name, host, int(tcp_port), int(http_port)))
        return nodes

    def get_node_info(ip) -> NodeInfo:
        with open('network_info.csv') as file:
            for line in file:
                if line[0] != '#': # jump comments
                    (name, host, tcp_port, http_port) = line.split(',')
                    if host == ip:
                        return NodeInfo(name, host, int(tcp_port), int(http_port))
