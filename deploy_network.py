# required imports
import os
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

# interface helper
iface_1_helper = client.InterfaceHelper(ip4_prefix="10.0.0.0/24", ip6_prefix="2001::/64")
iface_2_helper = client.InterfaceHelper(ip4_prefix="10.0.1.0/24", ip6_prefix="2001::/64")

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

# create router
position = Position(x=400, y=100)
router = Node(type=NodeType.DEFAULT, position=position, model="router", name="R1")
response = core.add_node(session_id, router)
router_id = response.node_id

# create switch nodes
position = Position(x=200, y=100)
switch_1 = Node(type=NodeType.SWITCH, position=position, name="S1")
response = core.add_node(session_id, switch_1)
switch1_id = response.node_id

position = Position(x=600, y=100)
switch_2 = Node(type=NodeType.SWITCH, position=position, name="S2")
response = core.add_node(session_id, switch_2)
switch2_id = response.node_id

# create nodes 
nodes = []

position = Position(x=100, y=200)
n1 = Node(type=NodeType.DEFAULT, position=position, model="host", name="F1", services=["DefaultRoute", "SSH", "UserDefined"])
response = core.add_node(session_id, n1)
n1_id = response.node_id
nodes.append(n1_id)

position = Position(x=300, y=200)
n2 = Node(type=NodeType.DEFAULT, position=position, model="host", name="F2", services=["DefaultRoute", "SSH", "UserDefined"])
response = core.add_node(session_id, n2)
n2_id = response.node_id
nodes.append(n2_id)

position = Position(x=500, y=200)
n3 = Node(type=NodeType.DEFAULT, position=position, model="host", name="F3", services=["DefaultRoute", "SSH", "UserDefined"])
response = core.add_node(session_id, n3)
n3_id = response.node_id
nodes.append(n3_id)

position = Position(x=700, y=200)
n4 = Node(type=NodeType.DEFAULT, position=position, model="host", name="F4", services=["DefaultRoute", "SSH", "UserDefined"])
response = core.add_node(session_id, n4)
n4_id = response.node_id
nodes.append(n4_id)

configure_services(session_id, nodes)

# links switch to router
"""options = LinkOptions(
    bandwidth=0,
    delay=5000,
    dup=0,
    loss=0,
    jitter=0,
)"""

# iface1 = iface_1_helper.create_iface(router_id, 0)
#core.add_link(session_id, router_id, switch1_id, iface1, options= options)
iface_data = Interface(id=0, ip4="10.0.0.1", ip4_mask=24, ip6="2001::", ip6_mask=64,)
core.add_link(session_id, router_id, switch1_id, iface_data)

# iface1 = iface_2_helper.create_iface(router_id, 1)
iface_data = Interface(id=1, ip4="10.0.1.1", ip4_mask=24, ip6="2001::", ip6_mask=64,)
core.add_link(session_id, router_id, switch2_id, iface_data)

# links nodes to switch

# iface1 = iface_1_helper.create_iface(n1_id, 0)
iface_data = Interface(ip4="10.0.0.2", ip4_mask=24, ip6="2001::", ip6_mask=64,)
core.add_link(session_id, n1_id, switch1_id, iface_data)

# iface1 = iface_1_helper.create_iface(n2_id, 0)
iface_data = Interface(ip4="10.0.0.3", ip4_mask=24, ip6="2001::", ip6_mask=64,)
core.add_link(session_id, n2_id, switch1_id, iface_data)

# iface1 = iface_2_helper.create_iface(n3_id, 0)
iface_data = Interface(ip4="10.0.1.2", ip4_mask=24, ip6="2001::", ip6_mask=64,)
core.add_link(session_id, n3_id, switch2_id, iface_data)
# iface1 = iface_2_helper.create_iface(n4_id, 0)
iface_data = Interface(ip4="10.0.1.3", ip4_mask=24, ip6="2001::", ip6_mask=64,)
core.add_link(session_id, n4_id, switch2_id, iface_data)

# change session state
core.set_session_state(session_id, SessionState.INSTANTIATION)

while(True):
    cmd = input('Enter "end" to kill core_session: ')
    if cmd == "end":
        shutdown_session(session_id)
        break