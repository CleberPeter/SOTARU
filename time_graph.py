from typing import List
import numpy as np
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

class Event_Type:
    def __init__(self, name, color):
        self.name = name
        self.color = color

class Event:
    def __init__(self, init, size, type):
        self.init = init
        self.size = size
        self.type = EVENT_TYPE_FOLLOWER

        for event_type in event_types:
            if type == event_type.name:
                self.type = event_type
                break

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
    def __init__(self, origin : Node, destiny : Node, type, send_time, receive_time):
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
                patch_handles.append(self.graph.barh(idx_node, event.size, left = event.init, color = event.type.color, align='center'))
                patch = patch_handles[-1][0] 
                bl = patch.get_xy()
                x = 0.5*patch.get_width() + bl[0]
                y = 0.5*patch.get_height() + bl[1]
                node.set_y_pos(y)
                self.graph.text(x, y, event.type.name, ha='center',va='center', color='white')
    
    def plot_messages(self):
        for message in self.messages:
            origin_y_pos = message.origin.y_pos
            destiny_y_pos = message.destiny.y_pos
            len_arrow = destiny_y_pos - origin_y_pos
            diff_time = message.receive_time - message.send_time
            self.graph.arrow(message.send_time, origin_y_pos, diff_time, len_arrow, color = 'gray', width = 0.015, head_width = 0.06)

    def plot_legend(self):
        self.graph.set_xlabel('miliseconds')
        y_pos = np.arange(len(self.nodes))
        self.graph.set_yticks(y_pos)
        self.graph.set_yticklabels([node.name for node in reversed(self.nodes)])

        patches = []
        for event_type in event_types:
            patches.append(mpatches.Patch(label=event_type.name, color=event_type.color))
        self.graph.legend(handles=patches)
    
    def plot(self):
        self.graph.clear()
        self.plot_events()
        self.plot_messages()
        self.plot_legend()

        plt.title('Events on SOTARU Infrastructure')
        plt.draw()
        plt.pause(0.0001)
    
    def plot_end(self):
        plt.show()

EVENT_TYPE_FOLLOWER = Event_Type('FOLLOWER', 'navy')
EVENT_TYPE_CANDIDATE = Event_Type('CANDIDATE', 'green')
EVENT_TYPE_LEADER = Event_Type('LEADER', 'red')

event_types : List[Event_Type] = []
event_types.append(EVENT_TYPE_FOLLOWER)
event_types.append(EVENT_TYPE_CANDIDATE)
event_types.append(EVENT_TYPE_LEADER)

"""time_graph = Time_Graph()
nodes_len = 42

# create nodes
for i in range(nodes_len):
    node_name = 'F' + str((i+1))
    time_graph.insert_node(node_name)
"""

# insert events
"""for i in range(7):
    if (i == 0):
        time_graph.nodes[i].insert_event(Event(0, 1, EVENT_TYPE_FOLLOWER))
        time_graph.nodes[i].insert_event(Event(1, 1, EVENT_TYPE_CANDIDATE))
        time_graph.nodes[i].insert_event(Event(2, 1, EVENT_TYPE_LEADER))
    else:
        time_graph.nodes[i].insert_event(Event(0, 3, EVENT_TYPE_FOLLOWER))
"""
"""time_graph.nodes[2].insert_event(Event(0, 732, 'FOLLOWER'))

time_graph.nodes[1].insert_event(Event(0, 255, 'FOLLOWER'))
time_graph.nodes[1].insert_event(Event(255, 1, 'CANDIDATE'))
time_graph.nodes[1].insert_event(Event(226, 501, 'LEADER'))

time_graph.nodes[0].insert_event(Event(0, 735, 'FOLLOWER'))

time_graph.nodes[3].insert_event(Event(0, 258, 'FOLLOWER'))
time_graph.nodes[3].insert_event(Event(258, 479, 'CANDIDATE'))
time_graph.nodes[3].insert_event(Event(737, 0, 'FOLLOWER'))
"""
# insert messages
# time_graph.insert_message(Message(time_graph.nodes[0], time_graph.nodes[6], 0.8, 0.8))
# time_graph.insert_message(Message(time_graph.nodes[0], time_graph.nodes[2], 0.8, 0.9))

# time_graph.plot()