from typing import List


class ManufacturerNode:
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

class SwitchNode:
    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.nodes : List[ManufacturerNode] = []

class RouterNode:
    def __init__(self, name):
        self.name = name
        self.switchs : List[SwitchNode] = []

class Network:
    def __init__(self, file_path):
        self.routers : List[RouterNode] = []
        with open(file_path) as file:
            for line in file:
                if line[0] == 'R':
                    name = line
                    self.routers.append(RouterNode(name))
                elif line[0] == 'S':
                    (name, host) = line.split(',')
                    router = self.routers[-1]
                    router.switchs.append(SwitchNode(name, host))
                elif line[0] == 'F':
                    (name, host, tcp_port, http_port) = line.split(',')
                    router = self.routers[-1]
                    switch = router.switchs[-1]
                    switch.nodes.append(ManufacturerNode(name, host, int(tcp_port), int(http_port)))


    def get_manufacturer_nodes(self) -> List[ManufacturerNode]:
        nodes : List[ManufacturerNode] = []
        for router in self.routers:
            for switch in router.switchs:
                for node in switch.nodes:
                    nodes.append(node)
        return nodes

    def get_manufacturer_node_info(self, ip) -> ManufacturerNode:
        nodes = self.get_manufacturer_nodes()
        for node in nodes:
            if node.host == ip:
                return node
        return None
