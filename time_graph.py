from typing import List
import numpy as np
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from enum import Enum

class Message_Types(Enum):
    request_vote = 1
    request_vote_answer = 2
    append_entries = 3
    append_entries_answer = 4

class Raft_States(Enum):
    FOLLOWER = 1, 'navy'
    CANDIDATE = 2, 'green'
    LEADER = 3, 'red'
    
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

        self.fig = plt.figure()
        self.graph = self.fig.add_subplot(111)
        self.ann_list = []
        matplotlib.rcParams['figure.raise_window'] = False # disable autofocus on figure

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
                patch_handles.append(self.graph.barh(idx_node, event.size, left = event.init, color = event.raft_state.color, align='center'))
                patch = patch_handles[-1][0] 
                bl = patch.get_xy()
                x = 0.5*patch.get_width() + bl[0]
                y = 0.5*patch.get_height() + bl[1]
                node.set_y_pos(y)
                self.graph.text(x, y, event.raft_state.name, ha='center',va='center', color='white')
    
    def plot_messages(self):
        for message in self.messages:
            origin_y_pos = message.origin.y_pos
            destiny_y_pos = message.destiny.y_pos
            ann = plt.annotate(message.type.value, verticalalignment="center", xy=(message.send_time, origin_y_pos), xytext=(message.receive_time, destiny_y_pos), arrowprops=dict(arrowstyle="<-"))
            self.ann_list.append(ann)

    def plot_legend(self):
        self.graph.set_xlabel('miliseconds')
        y_pos = np.arange(len(self.nodes))
        self.graph.set_yticks(y_pos)
        self.graph.set_yticklabels([node.name for node in reversed(self.nodes)])
        
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

    def clean_plot(self):
        for ann in self.ann_list:
            ann.remove()
        self.ann_list = []
        self.graph.clear()
        
    def plot(self):
        
        self.clean_plot()

        self.plot_events()
        self.plot_messages()
        self.plot_legend()

        plt.title('Events on SOTARU Infrastructure')
        plt.draw()
        plt.pause(0.0001)
    
    def plot_end(self):
        plt.show()
