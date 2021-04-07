def get():

    nodes = []

    with open('nodes.csv') as file:
        for line in file:
            (name, host, tcp_port, http_port) = line.split(',')
            if name != "name":  # ignore header
                nodes.append(NodeInfo(name, host, int(
                    tcp_port), int(http_port)))

    return nodes


class NodeInfo:
    def __init__(self, name, host, tcp_port, http_port):
        self.name = name
        self.host = host
        self.tcp_port = tcp_port
        self.http_port = http_port
