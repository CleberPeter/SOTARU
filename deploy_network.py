# required imports
import os
import numpy as np
from network import Network
from time import sleep
from core.api.grpc import client
from core.api.grpc.core_pb2 import Node, NodeType, Position, SessionState, LinkOptions, Interface

raft_files = ["tcp_logger.py", "crypto.py", "tcp_client.py", "network_info.csv", "tcp_server.py"]
raft_files.extend(["start_sotaru_service.sh", "node.py", "file_logger.py", "logger_server_info.csv"])
raft_files.extend(["network.py", "raft.py", "tcp_logger_server_info.py", "helper.py", "http_server.py", "logger.py"])
service_name = "UserDefined"
startup_service_cmd = "bash start_sotaru_service.sh"

def get_file_content(relative_path):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, relative_path)
    
    f = open(filename)
    content = f.read()
    
    f.close()
    return str(content)

def configure_services(session_id, nodes):
    
    for node in nodes:
        core.set_node_service(
            session_id,
            node,
            service_name,
            files = raft_files,
            directories=[],
            startup=[startup_service_cmd],
            validate=[],
            shutdown=[],
        )

        for file in raft_files:
            core.set_node_service_file(
                session_id,
                node,
                service_name,
                file,
                get_file_content(file),
            )

def shutdown_session(session_id):
    print('ending core session ' + str(session_id))
    core.stop_session(session_id)
    core.delete_session(session_id)

network = Network('network_info.csv')

# create grpc client and connect
core = client.CoreGrpcClient()
core.connect()

# kill older sessions
response = core.get_sessions()
for session in response.sessions:
    shutdown_session(session.id)

# create session and get id
response = core.create_session()
session_id = response.session_id

# change session state to configuration so that nodes get started when added
core.set_session_state(session_id, SessionState.CONFIGURATION)

# create network
radius = 150
center = Position(x=500, y=350)
node_ids = []
for router in network.routers:
    router_position = center
    core_router = Node(type=NodeType.DEFAULT, position=router_position, model="router", name=router.name)
    response = core.add_node(session_id, core_router)
    router.set_id(response.node_id)

    switchs_qty = len(router.switchs)
    if switchs_qty:
        switch_rot_degree_steps = 360/switchs_qty
        for idx, switch in enumerate(router.switchs):
            switch_rot_degree = idx*switch_rot_degree_steps
            x = radius * np.cos(np.deg2rad(switch_rot_degree)) + center.x
            y = radius * np.sin(np.deg2rad(switch_rot_degree)) + center.y
            
            switch_position = Position(x=x, y=y)
            core_switch = Node(type=NodeType.SWITCH, position=switch_position, name=switch.name)
            response = core.add_node(session_id, core_switch)
            switch.set_id(response.node_id)

            nodes_qty = len(switch.nodes)
            if nodes_qty:
                node_rot_degree_steps = 90/nodes_qty
                for idx, node in enumerate(switch.nodes):
                    node_rot_degree = (idx*node_rot_degree_steps) + switch_rot_degree - 45
                    x = radius * np.cos(np.deg2rad(node_rot_degree)) + switch_position.x
                    y = radius * np.sin(np.deg2rad(node_rot_degree)) + switch_position.y
                    
                    node_position = Position(x=x, y=y)
                    core_node = Node(type=NodeType.DEFAULT, position=node_position, model="host", name=node.name, services=["DefaultRoute", "SSH", "UserDefined"])
                    response = core.add_node(session_id, core_node)
                    node.set_id(response.node_id)
                    node_ids.append(response.node_id)

configure_services(session_id, node_ids)

link_configs = []

# link configs
for i in range(4):
    link_config = LinkOptions(bandwidth=0, delay=int(i*100e3), dup=0, loss=0, jitter=0,)
    link_configs.append(link_config)

# link switches to routers
for router in network.routers:
    for router_idx, switch in enumerate(router.switchs):
        iface_data = Interface(id=router_idx, ip4=switch.host, ip4_mask=24, ip6="2001::", ip6_mask=64,)
        # core.add_link(session_id, router.id, switch.id, iface_data, options=link_configs[router_idx])
        core.add_link(session_id, router.id, switch.id, iface_data)

        # link nodes to switches
        for node_idx,node in enumerate(switch.nodes):
            option = LinkOptions(bandwidth=0, delay=int(node_idx*10e3), dup=0, loss=0, jitter=0,)
            iface_data = Interface(ip4=node.host, ip4_mask=24, ip6="2001::", ip6_mask=64,)
            # core.add_link(session_id, node.id, switch.id, iface_data, options=option)
            core.add_link(session_id, node.id, switch.id, iface_data)

# change session state
core.set_session_state(session_id, SessionState.INSTANTIATION)

while(True):
    cmd = input('Enter "end" to kill core_session: ')
    if cmd == "end":
        shutdown_session(session_id)
        break