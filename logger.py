from helper import Helper

class Logger:
    def __init__(self, name):
        self.name = name
    
    def prepare(self, data):
        datetime_str = Helper.get_datetime()
        log_data = '[' + datetime_str + '] - ' + '[' + self.name + '] - '  + data
        print(log_data)
        return log_data