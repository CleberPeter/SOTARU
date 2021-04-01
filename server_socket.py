import socket
from threading import Thread


class ServerSocket:

    def __init__(self, port, on_receive):

        #print('SERVER_SOCKET: init, port: ', port)

        self.port = port
        self.on_receive = on_receive

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', self.port))
        self.socket.listen()

        self.thread = Thread(target=self.wait_connections, args=())
        self.thread.start()

    def wait_connections(self):

        while True:
            (clientsocket, address) = self.socket.accept()
            #print('SERVER_SOCKET: new connection, address: ', address)

            Client(clientsocket, address, self.on_receive)

class Client:

    def __init__(self, socket, address, on_receive):

        self.address = address
        self.socket = socket
        self.on_receive = on_receive
        self.thread = Thread(target=self.receive, args=())
        self.thread.start()

    def receive(self):

        while True:
            chunks = []
            chunk = ''
            bytes_recd = 0

            while True:

                try:
                    chunk = self.socket.recv(1)
                    if chunk != b'\n':
                        if chunk != b'':
                            chunks.append(chunk)
                        else:
                            # print('SERVER_SOCKET: client broken, address: ', self.address)
                            return 0
                    else:
                        break

                except Exception:  # connection closed
                    return 0

            self.on_receive(self, b''.join(chunks))

    def send(self, data):
        data += '\n'
        bata_b = data.encode()

        if self.socket.send(bata_b) != 0:
            return True
        else:
            return False
