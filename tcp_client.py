import socket
from threading import Thread


class TcpClient:

    def __init__(self, host, port, on_receive):

        # print('CLIENT_SOCKET: init, host:' + host + ', port: ' + str(port))

        self.port = port
        self.host = host
        self.on_receive = on_receive

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((self.host, self.port))

        self.thread = Thread(target=self.receive, args=())
        self.thread.start()

    def receive(self):

        while True:
            chunks = []
            chunk = ''

            while True:
                try:
                    chunk = self.socket.recv(1)
                    if chunk != b'\n':
                        if chunk != b'':
                            chunks.append(chunk)
                        else:
                            # print('CLIENT_SOCKET: client broken, address: ', self.address)
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

    def close(self):

        self.socket.close()
