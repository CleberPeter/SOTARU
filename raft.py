import json
from threading import Timer
from random import randint
import network
from tcp_server import TcpServer
from tcp_client import TcpClient
from current_state_db import Current_State_DB

# ms
MIN_RANDOM_TIMEOUT = 100
MAX_RANDOM_TIMEOUT = 300
# s
DEFAULT_TIMEOUT = 1
HEARTBEAT_TIMEOUT = 0.5


class Raft:

    def __init__(self, name, tcp_sever_port, force_leader=False):

        self.current_term = 0
        self.voted_for = ''
        self.votes = 0
        self.name = name
        self.sm = "FOLLOWER"
        self.force_leader = force_leader

        self.current_state_db = Current_State_DB(name)
        self.server = TcpServer(tcp_sever_port, self.server_on_receive)

        self.timer = Timer(DEFAULT_TIMEOUT, self.timeout_handle, [])
        self.timer.start()

    def parser(self, socket, data):

        msg = data.decode("utf-8")
        print("NODE_" + self.name + ": receive, data: " + msg)

        fields = msg.split(';')
        cmd = fields[0]
        name = fields[1]
        term = int(fields[2])

        if cmd == "request_vote":
            if term > self.current_term:
                # TODO: or (check log index to)
                if self.voted_for == '' or True:
                    self.current_term = term
                    self.voted_for = name
                    self.sm = "FOLLOWER"
                    voted = True
            else:
                voted = False

            self.send_request_votes_answer(socket, voted)

        elif cmd == "request_vote_answer":

            status_vote = fields[3]
            if status_vote == "true":
                self.votes += 1
                nodes = network.get_info()

                if self.votes > len(nodes)/2:
                    self.sm = "LEADER"

        elif cmd == "append_entries":

            if term >= self.current_term:
                self.current_term = term
                self.voted_for = name
                self.sm = "FOLLOWER"
                accept = True
            else:
                accept = False

            self.send_append_entries_answer(socket, accept)

    def i_am_leader(self):
        return self.sm == "LEADER"

    def publish(self, typ, data):

        if self.i_am_leader():
            self.send_append_entries(json.dumps(data))
            return (True, '')
        else:
            # For now only the leader can process the customer's messages.
            # Subsequently, the other nodes acted as proxy's directing messages
            # from customers to the leader.
            return (False, 'proxy function not implemented yet. Leader is: ' + self.voted_for)

        """
        if typ == "add_author":
            return self.current_state_db.insert_author(data)
        else:
            return (False, 'action not recognitzed.')
        """

    def server_on_receive(self, client, data):

        self.reinit_timer()
        self.parser(client, data)

    def client_on_receive(self, server, data):

        self.parser(server, data)
        server.close()

    def reinit_timer(self, time=1):

        self.timer.cancel()
        self.timer = Timer(time, self.timeout_handle, [])
        self.timer.start()

    def send_broadcast(self, msg):

        nodes = network.get_info()
        for node in nodes:
            if node.name != self.name:  # do not send to myself
                try:
                    socket = TcpClient(
                        node.host, node.tcp_port, self.client_on_receive)
                except Exception:  # fail to connect
                    continue

                socket.send(msg)

    def send_request_votes(self):

        # TODO: insert last_log_term_index and last_log_term
        msg = "request_vote;" + self.name + ";" + str(self.current_term)
        self.send_broadcast(msg)

    def send_request_votes_answer(self, socket, voted):

        if voted:
            voted = ";true"
        else:
            voted = ";false"

        msg = "request_vote_answer;" + self.name + ";"
        msg += str(self.current_term) + voted
        socket.send(msg)

    def send_append_entries(self, data):

        if self.i_am_leader():
            
            msg = "append_entries;" + self.name + ';'
            msg += str(self.current_term) + ';' + data
            self.send_broadcast(msg)
        else:
            return False

    def send_append_entries_answer(self, socket, accept):

        if accept:
            accept = ";true"
        else:
            accept = ";false"

        msg = "append_entries_answer;" + self.name + \
            ";" + str(self.current_term) + accept
        socket.send(msg)

    def timeout_handle(self):
        print("NODE_" + self.name + " raft task, sm: " + self.sm)

        if self.sm == "FOLLOWER":

            self.voted_for = ''
            self.sm = "CANDIDATE"

            if self.force_leader:  # force to be a leader ?
                self.timeout_handle()
            else:
                timeout = randint(MIN_RANDOM_TIMEOUT, MAX_RANDOM_TIMEOUT)/1000
                self.reinit_timer(timeout)

        elif self.sm == "CANDIDATE":

            if self.voted_for == '':

                self.current_term += 1
                self.voted_for = self.name
                self.votes = 1

                self.reinit_timer()
                self.send_request_votes()
            else:
                # election end without me becoming leader
                self.sm = "FOLLOWER"
                self.timeout_handle()

        elif self.sm == "LEADER":

            self.reinit_timer(HEARTBEAT_TIMEOUT)
            self.send_append_entries('')  # only heartbeat
