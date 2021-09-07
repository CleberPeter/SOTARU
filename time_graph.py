from typing import List
import numpy as np
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from enum import Enum

WINDOW_SIZE = 5000 # ms

class Message_Types(Enum):
    request_vote = 1
    request_vote_answer = 2
    append_entries = 3
    append_entries_answer = 4
    fail_connect = 5

class Raft_States(Enum):
    FOLLOWER = 1, 'navy'
    CANDIDATE = 2, 'green'
    LEADER = 3, 'red'
    OFFLINE = 4, 'black'
    
    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str, color: str = None):
        self._color_ = color

    def __str__(self):
        return self.value

    # this makes sure that the attribute is read-only
    @property
    def color(self):
        return self._color_

class Event:
    def __init__(self, init, size, raft_state : Raft_States):
        self.init = init
        self.size = size
        self.raft_state = raft_state

class Node:
    def __init__(self, name):
        self.name = name
        self.events : List[Event] = []
        self.y_pos = 0

    def insert_event(self, event: Event):
        last_event = self.get_last_event()
        if last_event: # connect events
            self.update_event(last_event, event.init)
        self.events.append(event)

    def update_event(self, event: Event, ms):
        event.size = ms - event.init

    def get_last_event(self):
        if len(self.events):
            return self.events[-1]
        else:
            return None

    def set_y_pos(self, val):
        self.y_pos = val

class Message:
    def __init__(self, origin : Node, destiny : Node, type : Message_Types, send_time, receive_time):
        self.origin = origin
        self.destiny = destiny
        self.type = type
        self.send_time = send_time
        self.receive_time = receive_time

class Time_Graph:
    def __init__(self):
        self.nodes : List[Node] = []
        self.messages : List[Message] = []
        self.removable_list = []
        self.last_idx_msgs = 0
        self.last_ms = 0

        self.fig = plt.figure()
        self.graph = self.fig.add_subplot(111)
        matplotlib.rcParams['figure.raise_window'] = False # disable autofocus on figure
        self.graph.patch.set_facecolor('gray')
        self.graph.patch.set_alpha(0.5)

    def insert_node(self, name):
        self.nodes.append(Node(name))

    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node

        self.insert_node(name)
        return self.get_node(name)

    def has_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return True
        return False

    def insert_message(self, message : Message):
        self.messages.append(message)

    def plot_events(self):
        patch_handles = []
        for idx_node, node in enumerate(reversed(self.nodes)):
            for event in node.events:
                last_ms = event.init + event.size
                if last_ms > self.last_ms:
                    self.last_ms = last_ms

                barh = self.graph.barh(idx_node, event.size, left = event.init, color = event.raft_state.color, align='center')
                patch_handles.append(barh)
                patch = patch_handles[-1][0] 
                bl = patch.get_xy()
                x = 0.5*patch.get_width() + bl[0]
                y = 0.5*patch.get_height() + bl[1]
                node.set_y_pos(y)
                
                self.removable_list.append(barh)
                
    def plot_messages(self):
        idx = 0
        for idx, message in enumerate(self.messages):
            if not self.last_idx_msgs or idx > self.last_idx_msgs:
                origin_y_pos = message.origin.y_pos
                destiny_y_pos = message.destiny.y_pos
                plt.annotate(message.type.value, color = 'white', verticalalignment="center", xy=(message.receive_time, destiny_y_pos), xytext=(message.send_time, origin_y_pos), arrowprops=dict(arrowstyle="->", color='white'))
                
        self.last_idx_msgs = idx

    def plot_node_name_legend(self):
        y_pos = np.arange(len(self.nodes))
        self.graph.set_yticks(y_pos)
        self.graph.set_yticklabels([node.name for node in reversed(self.nodes)])
        
    def plot_legend(self):
        self.graph.set_xlabel('miliseconds')
        self.plot_node_name_legend()

        patches = []
        for raft_state in Raft_States:
            patches.append(mpatches.Patch(label=raft_state.name, color=raft_state.color))
        leg1 = self.graph.legend(handles = patches)

        proxies = []
        labels = []
        for message_type in Message_Types:
            proxies.append(matplotlib.lines.Line2D([0], [0], linestyle='none', mfc='black',
                mec='none', marker=r'$\mathregular{{{}}}$'.format(message_type.value)))
            labels.append(message_type.name)

        self.graph.legend(proxies, labels, loc="lower left")    
        self.graph.add_artist(leg1)
        
    def plot_init(self):
        self.plot_legend()
        plt.title('Events on SOTARU Infrastructure')
    
    def plot_clean(self):
        for removable_item in self.removable_list:
            removable_item.remove()
        self.removable_list[:] = []

    def plot_adjust_limits(self, inf_limit, sup_limit):
        plt.xlim(inf_limit, sup_limit)

    def update_offline_nodes(self):
        for node in self.nodes:
            last_event = node.get_last_event()
            if last_event and last_event.raft_state == Raft_States.OFFLINE:
                node.update_event(last_event, self.last_ms)

    def plot(self):
        self.update_offline_nodes()
        self.plot_node_name_legend()
        
        inf_limit = self.last_ms - WINDOW_SIZE
        if inf_limit < 0:
            inf_limit = 0

        sup_limit = self.last_ms
        if sup_limit < WINDOW_SIZE:
            sup_limit = WINDOW_SIZE

        self.plot_adjust_limits(inf_limit, sup_limit)

        self.plot_clean()
        self.plot_events()
        self.plot_messages()
        
        plt.draw()
        plt.pause(0.0001)
    
    def plot_update_limits(self, inf_limit, sup_limit):
        self.plot_adjust_limits(inf_limit, sup_limit)
        plt.draw()

    def plot_end(self):
        plt.show()
