from threading import Timer
from random import randint
from server_socket import ServerSocket
from client_socket import ClientSocket
import nodes_info as nodes_info

MIN_WAIT_TIME = 100
MAX_WAIT_TIME = 300


class Raft:

    def __init__(self, name, sever_port):
        self.current_term = 0
        self.voted_for = ''
        self.votes = 0
        self.name = name
        self.sm = "FOLLOWER"

        self.server = ServerSocket(sever_port, self.server_on_receive)

        timeout = 1
        self.timer = Timer(timeout, self.task, [])
        self.timer.start()

    def server_on_receive(self, client, data):
        self.reinit_timer()

        msg = data.decode("utf-8")
        print("NODE_" + self.name + ": receive, data: " + msg)

        fields = msg.split(';')
        name = fields[1]
        term = int(fields[2])

        if fields[0] == "request_vote":

            if self.voted_for == '' and self.current_term < term:
                self.current_term = term
                self.voted_for = name
                self.sm = "FOLLOWER"
                status = ";true"
            else:
                status = ";false"

            msg = "vote;" + str(self.current_term) + status
            client.send(msg)

        elif fields[0] == "append_entries":
            if self.current_term <= term:
                self.current_term = term
                self.voted_for = name
                self.sm = "FOLLOWER"

    def client_on_receive(self, server, data):

        msg = data.decode("utf-8")
        print("NODE_" + self.name + ": receive, data: " + msg)

        fields = msg.split(';')

        if fields[0] == "vote":
            status_vote = fields[2]

            if status_vote == "true":
                self.votes += 1
                nodes = nodes_info.get()

                if self.votes > len(nodes)/2:
                    self.sm = "LEADER"

            server.close()

    def reinit_timer(self, time=1):
        self.timer.cancel()
        self.timer = Timer(time, self.task, [])
        self.timer.start()

    def send_broadcast(self, msg):
        nodes = nodes_info.get()
        for node in nodes:
            if node.name != self.name:  # do not send to myself
                socket = ClientSocket(
                    node.host, node.port, self.client_on_receive)
                socket.send(msg)

    def send_request_votes(self):
        # TODO: insert last_log_term_index and last_log_term
        msg = "request_vote;" + self.name + ";" + str(self.current_term)
        self.send_broadcast(msg)

    def send_heartbeat(self):
        msg = "append_entries;" + self.name + ';' + str(self.current_term)
        self.send_broadcast(msg)

    def task(self):
        print("NODE_" + self.name + " raft task, sm: " + self.sm)

        if self.sm == "FOLLOWER" or self.sm == "CANDIDATE":

            self.sm = "PRE-CANDIDATE"
            self.voted_for = ''
            timeout = randint(MIN_WAIT_TIME, MAX_WAIT_TIME)/1000
            self.reinit_timer(timeout)

        elif self.sm == "PRE-CANDIDATE":

            self.sm = "CANDIDATE"
            self.current_term += 1
            self.voted_for = self.name
            self.votes = 1
            self.reinit_timer()

            self.send_request_votes()

        elif self.sm == "LEADER":
            timeout = 0.5
            self.reinit_timer(timeout)
            self.send_heartbeat()
