from helper import Helper

class Logger:
    def __init__(self, name, enable_console = True):
        self.name = name
        self.enable_console = enable_console

    def prepare(self, data):
        datetime_str = Helper.get_datetime()
        log_data = '[' + datetime_str + '] - ' + '[' + self.name + '] - '  + data
        if self.enable_console:
            print(log_data)
        return log_data