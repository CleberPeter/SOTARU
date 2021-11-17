from typing import List

class Node:
    def __init__(self, name, host, tcp_port, http_port):
        self.name = name
        self.host = host
        self.id = 0
        self.tcp_port = tcp_port
        self.http_port = http_port
        self.external_ip = ''

    def set_id(self, id):
        self.id = id
    
    def get_str_info(self):
        ret = 'name: ' + self.name + ', '
        ret += 'host: ' + self.host + ', '
        ret += 'external_ip: ' + self.external_ip + ', '
        ret += 'tcp_port: ' + str(self.tcp_port) + ', '
        ret += 'http_port: ' + str(self.http_port)
        return ret

class ManufacturerNode(Node):
    def __init__(self, name, host, tcp_port, http_port):
        super().__init__(name, host, tcp_port, http_port)
        self.clients : List[ManufacturerNode] = []

class ClientNode(Node):
    def __init__(self, name, host, tcp_port, http_port, node : ManufacturerNode):
        super().__init__(name, host, tcp_port, http_port)
        self.father_node : ManufacturerNode = node
        
class SwitchNode:
    def __init__(self, name, host):
        self.name = name
        self.id = 0
        self.host = host
        self.nodes : List[ManufacturerNode] = []

    def set_id(self, id):
        self.id = id

class RouterNode:
    def __init__(self, name):
        self.name = name
        self.id = 0
        self.switchs : List[SwitchNode] = []

    def set_id(self, id):
        self.id = id

class Network:
    def __init__(self, file_path):
        self.routers : List[RouterNode] = []
        with open(file_path) as file:
            for line in file:
                if line[0] == 'R':
                    name = line.split('\n')[0]
                    self.routers.append(RouterNode(name))
                elif line[0] == 'S':
                    (name, host) = line.split(',')
                    host = host.split('\n')[0]
                    router = self.routers[-1]
                    router.switchs.append(SwitchNode(name, host))
                elif line[0] == 'F':
                    (name, host, tcp_port, http_port) = line.split(',')
                    router = self.routers[-1]
                    switch = router.switchs[-1]
                    switch.nodes.append(ManufacturerNode(name, host, int(tcp_port), int(http_port)))
                elif line[0] == 'C':
                    (name, host, tcp_port, http_port) = line.split(',')
                    router = self.routers[-1]
                    switch = router.switchs[-1]
                    node = switch.nodes[-1]
                    node.clients.append(ClientNode(name, host, int(tcp_port), int(http_port), node))


    def get_manufacturer_nodes(self) -> List[ManufacturerNode]:
        nodes : List[ManufacturerNode] = []
        for router in self.routers:
            for switch in router.switchs:
                for node in switch.nodes:
                    nodes.append(node)
        return nodes

    def get_client_nodes(self) -> List[ClientNode]:
        clients : List[ClientNode] = []
        for router in self.routers:
            for switch in router.switchs:
                for node in switch.nodes:
                    for client in node.clients:
                        clients.append(client)
        return clients

    def get_manufacturer_nodes_len(self):
        nodes = self.get_manufacturer_nodes()
        return len(nodes)

    def get_manufacturer_node_info(self, internal_ip, external_ip) -> ManufacturerNode:
        nodes = self.get_manufacturer_nodes()
        for node in nodes:
            if node.host == internal_ip:
                node.external_ip = external_ip
                return node
        return None

    def get_manufacturer_node(self, name) -> ManufacturerNode:
        nodes = self.get_manufacturer_nodes()
        for node in nodes:
            if node.name == name:
                return node
        return None

    def get_client_node_info(self, internal_ip, external_ip) -> ManufacturerNode:
        nodes = self.get_client_nodes()
        for node in nodes:
            if node.host == internal_ip:
                node.external_ip = external_ip
                return node
        return None
