import os
import json
import crypto
import time
from threading import Timer
from random import randint
from typing import List
from network import ManufacturerNode, Network
from tcp_server import Tcp_Server
from tcp_client import Tcp_Client
from tcp_logger import Tcp_Logger
from threading import Thread
from copy import deepcopy
# from current_state_db import Current_State_DB

# ms
MIN_RANDOM_TIMEOUT = 100
MAX_RANDOM_TIMEOUT = 300
# s
DEFAULT_TIMEOUT = 1
HEARTBEAT_TIMEOUT = 0.5

class Follower:
    def __init__(self, info : ManufacturerNode, next_index=0):
        self.info = info
        self.next_index = next_index

class Log:
    def __init__(self, data, term, acks=0):
        self.data = data
        self.term = term
        self.acks = acks

class Message:
    def __init__(self, type, sender, leader_term, receiver, prev_index, prev_term, data, data_term):
        self.type = type
        self.sender = sender
        self.leader_term = leader_term
        self.receiver = receiver
        self.prev_index = prev_index
        self.prev_term = prev_term
        self.data = data
        self.data_term = data_term

    def from_csv(csv_data):
        fields = str.split(csv_data, ';')
        
        id = int(fields[0])
        type = fields[1]
        sender = fields[2] 
        leader_term = int(fields[3])
        receiver = fields[4] 
        prev_index = int(fields[5])
        prev_term = int(fields[6])
        data = fields[7]
        data_term = int(fields[8])

        msg = Message(type, sender, leader_term, receiver, prev_index, prev_term, data, data_term)
        msg.id = id

        return msg

    def to_csv(self):
        csv = self.type + ';' + self.sender + ';' + str(self.leader_term) + ';'
        csv += self.receiver + ';' + str(self.prev_index) + ';' + str(self.prev_term) + ';'
        csv += self.data + ';' + str(self.data_term)
        self.id = crypto.CRC32(str(time.time()) + csv)
        csv = str(self.id) + ';' + csv
        return csv

class Raft:
    def __init__(self, name, network : Network, tcp_sever_port, tcp_logger : Tcp_Logger, force_leader=False):

        self.current_term = 0
        self.voted_for = ''
        self.votes = 0
        self.name = name
        self.sm = "FOLLOWER"
        self.tcp_logger = tcp_logger
        self.force_leader = force_leader
        self.suspended = False
        self.requesting_votes = [False]
        self.network = network

        self.logs : List[Log] = []
        self.followers : List[Follower] = []

        self.logs.append(Log('genesis_block', 0))
        self.logs.append(Log('boundary_condition', 0))

        # TODO: became followers list dynamic
        self.update_followers_list()

        # self.current_state_db = Current_State_DB(name)
        self.server = Tcp_Server(tcp_sever_port, self.server_on_receive)
        self.timer = Timer(DEFAULT_TIMEOUT, self.timeout_handle, [])
        
    def start(self):
        self.tcp_logger.save('[RAFT_SM] - ' + self.sm)
        self.timer.start()

    def is_heartbeat(self, data):
        return data == ''

    def stop_votes_request(self):
        self.requesting_votes[0] = False
    
    def start_votes_request(self):
        self.requesting_votes[0] = True

    def parser(self, socket, data):
        data_str = data.decode("utf-8")
        self.tcp_logger.save('[RECEIVED] - ' + data_str)

        msg : Message = Message.from_csv(data_str)

        if msg.type == "request_vote":
            leader_term = msg.leader_term
            leader_name = msg.sender
            
            # msg.prev_index
            # len(self.logs)

            if leader_term > self.current_term:
                # TODO: or (check log index to)
                if self.voted_for == '':
                    self.current_term = leader_term
                    self.voted_for = leader_name
                    self.sm = "FOLLOWER"
                    voted = True
                    self.stop_votes_request()
            else:
                voted = False

            self.send_request_votes_answer(socket, voted, leader_name)

        elif msg.type == "request_vote_answer":
            status_vote = msg.data
            if status_vote == "true":
                self.votes += 1
                nodes : List[ManufacturerNode] = self.network.get_manufacturer_nodes()

                if self.votes > len(nodes)/2:
                    leader_next_index = len(self.logs)

                    # this differs from the raft's original proposal, in
                    # which, the authors suggest that, after election, the
                    # next_index of the followers should be initialized with
                    # the same value as the leader. Creating this difference
                    # makes the leader when elected to check on network if
                    # there are followers out of date in relation to his log.
                    followers_next_index = leader_next_index - 1

                    self.update_followers_next_index(followers_next_index)
                    
                    # notify network that NOW i'm the leader
                    if self.sm != "LEADER":
                        self.sm = "LEADER"
                        self.stop_votes_request()
                        self.timeout_handle()

        elif msg.type == "append_entries":         
            leader_term = msg.leader_term
            leader_name = msg.sender

            accept = False
            next_index = len(self.logs)

            if leader_term >= self.current_term or self.voted_for == '':
                leader_prev_index = msg.prev_index
                leader_prev_term = msg.prev_term

                prev_term = self.logs[leader_prev_index].term

                # my log is consistent with leader ?
                # the previous log has to have same term of leader.
                if leader_prev_term == prev_term:
                    data = msg.data
                    data_term = msg.data_term

                    if not self.is_heartbeat(data):
                        leader_index = leader_prev_index + 1
                        index = next_index - 1

                        # already have an log in this position ?
                        if index >= leader_index:
                            term = self.logs[index].term

                            # this log is from another leader ?
                            if term != leader_term:

                                # delete all logs from now on
                                del self.logs[index:]
                                self.logs.append(Log(data, data_term))

                            # else: ignores the log, already added!
                        else:
                            self.logs.append(Log(data, data_term))

                    self.current_term = leader_term
                    self.voted_for = leader_name
                    self.sm = "FOLLOWER"
                    self.stop_votes_request()
                    accept = True

                self.send_append_entries_answer(socket, accept, leader_name)
            else:
                self.send_append_entries_answer(socket, accept, leader_name)
                # i must be the leader, my term is longer than that 
                # of the current leader.
                self.timeout_handle()

        elif msg.type == "append_entries_answer":
            accept = msg.data
            follower = self.find_follower(msg.sender)
            leader_next_index = len(self.logs)

            if accept == "True":
                if leader_next_index > follower.next_index:
                    follower.next_index += 1
            elif accept == "False" and follower.next_index > 0:
                follower.next_index -= 1

        self.tcp_logger.save('[RAFT_SM] - ' + self.sm)

    def find_follower(self, name):
        for follower in self.followers:
            if follower.info.name == name:
                return follower

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
    
    def suspend(self):
        self.timer.cancel()
        self.suspended = True
    
    def resume(self):
        self.suspended = False
        self.reinit_timer()

    def server_on_receive(self, client, data):
        if not self.suspended:
            self.reinit_timer()
            self.parser(client, data)

    def client_on_receive(self, server, data):
        if not self.suspended:
            self.parser(server, data)
            server.close()

    def reinit_timer(self, time=1):
        self.timer.cancel()
        self.timer = Timer(time, self.timeout_handle, [])
        self.timer.start()

    def log_fail_to_connect(self, node_destiny : ManufacturerNode, e : Exception):
        self.tcp_logger.save('[FAIL_CONNECT] - ' + node_destiny.name + ';' + str(e))
    
    def send_request_votes(self):        
        type = "request_vote"
        sender = self.name
        leader_term = self.current_term
        receiver = '' # will be filled by send_broadcast
        prev_index = len(self.logs) - 1
        prev_term = self.logs[prev_index].term
        data = ''
        data_term = self.current_term
        self.start_votes_request()

        msg = Message(type, sender, leader_term, receiver, prev_index, prev_term, data, data_term)
        self.send_broadcast(msg, self.requesting_votes)

    def send_request_votes_answer(self, socket, vote, node_destiny):
        if not vote:
            return

        type = "request_vote_answer"
        sender = self.name
        leader_term = self.current_term
        receiver = node_destiny
        prev_index = len(self.logs) - 1
        prev_term = self.logs[prev_index].term
        data = "true"
        data_term = self.current_term

        msg = Message(type, sender, leader_term, receiver, prev_index, prev_term, data, data_term)
        self.send(socket, msg)

    def send_append_entries(self, data):
        if self.i_am_leader():

            if not self.is_heartbeat(data):
                log = Log(data, self.current_term)
                self.logs.append(log)

            leader_next_index = len(self.logs)
            leader_term = self.current_term
            original_data = data

            for follower in self.followers:
                # follower have delayed logs?
                if follower.next_index != leader_next_index:
                    data = self.logs[follower.next_index].data
                    data_term = self.logs[follower.next_index].term
                    prev_index = follower.next_index - 1
                else:
                    data = original_data
                    data_term = leader_term
                    prev_index = leader_next_index - 1

                type = 'append_entries'
                prev_term = self.logs[prev_index].term
                sender = self.name
                receiver = follower.info.name

                msg = Message(type, sender, leader_term, receiver, prev_index, prev_term, data, data_term)
                Thread(target = self.send_to_node, args=(follower.info, msg, [1])).start()

            return True
        else:
            return False

    def send_append_entries_answer(self, socket, accept, node_destiny):
        type = "append_entries_answer"
        sender = self.name
        leader_term = self.current_term
        receiver = node_destiny
        prev_index = len(self.logs) - 1
        prev_term = self.logs[prev_index].term
        data = str(accept)
        data_term = self.current_term

        msg = Message(type, sender, leader_term, receiver, prev_index, prev_term, data, data_term)
        self.send(socket, msg)
    
    def send_broadcast(self, msg : Message, flux_control : list):
        nodes : List[ManufacturerNode] = self.network.get_manufacturer_nodes()
        for node in nodes:
            if node.name != self.name:  # do not send to myself
                msg.receiver = node.name
                Thread(target = self.send_to_node, args=(node, deepcopy(msg), flux_control)).start()
                
    def send_to_node(self, node : ManufacturerNode, msg : Message, flux_control : list):
        if not self.suspended:
            try:
                socket = Tcp_Client(node.host, node.tcp_port, self.client_on_receive)
                if flux_control[0]:
                    self.send(socket, msg)
            except Exception as e:  # fail to connect
                self.log_fail_to_connect(node, e)

    def send(self, socket, msg : Message):
        if not self.suspended:
            msg_str = msg.to_csv()
            self.tcp_logger.save('[SEND] - ' + msg_str)

            socket.send(msg_str)
                
    def update_followers_next_index(self, index):
        for follower in self.followers:
            follower.next_index = index

    def update_followers_list(self):
        # TODO: make followers list dynamic
        self.followers = []
        nodes : List[ManufacturerNode] = self.network.get_manufacturer_nodes()
        for node in nodes:
            if node.name != self.name:
                self.followers.append(Follower(node))

    def timeout_handle(self):
        self.tcp_logger.save('[RAFT_SM] - ' + self.sm)

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
                # election end without me becoming leader ? -> new election!
                # TODO: check if after a splitted election the term 
                # has to be incremented again for new election.
        
                self.sm = "FOLLOWER"
                self.timeout_handle()

        elif self.sm == "LEADER":
            self.reinit_timer(HEARTBEAT_TIMEOUT)
            self.send_append_entries('')  # empty data -> heartbeat
        