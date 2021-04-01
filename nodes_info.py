def get():
        
    nodes_info = []

    with open('nodes.csv') as file:
        for line in file:
            (name, host, port) = line.split(',')
            nodes_info.append(NodeInfo(name, host, int(port)))

    return nodes_info

class NodeInfo:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port