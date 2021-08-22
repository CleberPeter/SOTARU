import os
from logger import Logger

class File_Logger(Logger):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.file_name = name + '_log.txt'
        os.remove(self.file_name)

    def save(self, log_data):
        log_str = self.prepare(log_data)
        file = open(self.file_name, 'a')
        file.write(log_str + '\n')
        file.close()