from logger import Logger
from tcp_client import Tcp_Client
from tcp_logger_server_info import Tcp_Logger_Server_Info

class Tcp_Logger(Logger):
    def __init__(self, name):
        super().__init__(name)
        self.server_data = Tcp_Logger_Server_Info()
        self.tcp_client = Tcp_Client(self.server_data.host, self.server_data.port, None)

    def save(self, log_data) -> bool:
        log_str = self.prepare(log_data)
        return self.tcp_client.send(log_str)