from typing import List
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

class Event_Type:
    def __init__(self, name, color):
        self.name = name
        self.color = color

class Event:
    def __init__(self, init, size, type : Event_Type):
        self.init = init
        self.size = size
        self.type = type

class Node:
    def __init__(self, name):
        self.name = name
        self.events : List[Event] = []

    def insert_event(self, event: Event):
        self.events.append(event)

class Time_Graph:
    def __init__(self):
        self.nodes : List[Node] = []
    
    def insert_node(self, name):
        self.nodes.append(Node(name))

    def insert_event(self, node_name, event : Event):
        for node in self.nodes:
            if node_name == node.name:
                break
        
        node.insert_event(event)
    
    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        patch_handles = []

        for idx_node, node in enumerate(reversed(self.nodes)):
            for event in node.events:
                patch_handles.append(ax.barh(idx_node, event.size, left = event.init, color = event.type.color, align='center'))
                patch = patch_handles[-1][0] 
                bl = patch.get_xy()
                x = 0.5*patch.get_width() + bl[0]
                y = 0.5*patch.get_height() + bl[1]
                ax.text(x, y, event.type.name, ha='center',va='center', color='white')
                
        ax.set_xlabel('miliseconds')
        y_pos = np.arange(len(self.nodes))
        ax.set_yticks(y_pos)
        ax.set_yticklabels([node.name for node in reversed(self.nodes)])

        patches = []
        for event_type in event_types:
            patches.append(mpatches.Patch(label=event_type.name, color=event_type.color))
        ax.legend(handles=patches)
        plt.title('Events on SOTARU Infrastructure')
        plt.show()

EVENT_TYPE_FOLLOWER = Event_Type('Follower', 'navy')
EVENT_TYPE_CANDIDATE = Event_Type('Candidate', 'green')
EVENT_TYPE_LEADER = Event_Type('Leader', 'red')

event_types : List[Event_Type] = []
event_types.append(EVENT_TYPE_FOLLOWER)
event_types.append(EVENT_TYPE_CANDIDATE)
event_types.append(EVENT_TYPE_LEADER)

time_graph = Time_Graph()
nodes_len = 7

for i in range(nodes_len):
    node_name = 'F' + str((i+1))
    time_graph.insert_node(node_name)

    if (i == 0):
        time_graph.insert_event(node_name, Event(0, 1, EVENT_TYPE_FOLLOWER))
        time_graph.insert_event(node_name, Event(1, 1, EVENT_TYPE_CANDIDATE))
        time_graph.insert_event(node_name, Event(2, 1, EVENT_TYPE_LEADER))

for i in range(1, 7):
    node_name = 'F' + str((i+1))
    time_graph.insert_event(node_name, Event(0, 3, EVENT_TYPE_FOLLOWER))

time_graph.plot()