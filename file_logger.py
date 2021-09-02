import os
from logger import Logger

class File_Logger(Logger):
    def __init__(self, name, enable_console = True):
        super().__init__(name, enable_console)
        self.name = name
        self.file_name = name + '_log.txt'
        try:
            os.remove(self.file_name)
        except:
            pass
        
    def save(self, log_data):
        log_str = self.prepare(log_data)
        file = open(self.file_name, 'a')
        file.write(log_str + '\n')
        file.close()