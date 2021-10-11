import socket
import netifaces as ni
import time
from datetime import datetime


class Helper:
    def get_internal_ip():
        dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dummy_socket.connect(("8.8.8.8", 80))
        ip = dummy_socket.getsockname()[0]
        dummy_socket.close()

        return ip

    def get_external_ip():
        ni.ifaddresses('ctrl0')
        ip = ni.ifaddresses('ctrl0')[ni.AF_INET][0]['addr']

        return ip

    def get_datetime() -> str: 
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def get_timestamp() -> str: 
        return time.time()
