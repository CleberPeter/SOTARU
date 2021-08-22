import socket
from datetime import datetime

class Helper:
    def get_ip():
        dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dummy_socket.connect(("8.8.8.8", 80))
        ip = dummy_socket.getsockname()[0]
        dummy_socket.close()

        return ip

    def get_datetime() -> str: 
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

