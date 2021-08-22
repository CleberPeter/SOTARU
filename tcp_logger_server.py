from tcp_server import Tcp_Server
from tcp_logger_server_info import Tcp_Logger_Server_Info
from file_logger import File_Logger

def on_receive(self, log):
    
    log_str = log.decode("utf-8")
    print(log_str)
    file_logger.save(log_str)

if __name__ == "__main__":
    
    file_logger = File_Logger('server')
    tcp_logger_server_info = Tcp_Logger_Server_Info()
    tcp_server = Tcp_Server(tcp_logger_server_info.port, on_receive)
