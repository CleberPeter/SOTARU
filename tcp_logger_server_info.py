class Tcp_Logger_Server_Info:
    def __init__(self):
        with open('logger_server_info.csv') as file:
            for line in file:
                if line[0] != '#':  # jumo header
                    (host, port) = line.split(',')

        self.host = host
        self.port = int(port)