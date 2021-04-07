# dOTA

A distributed and fault-tolerant approach to the Over-The-Air (OTA) upgrade of embedded systems in compliance with the Internet Engineering Task Force (IETF) Secure Update Internet of Things [(SUIT)](https://datatracker.ietf.org/doc/draft-ietf-suit-architecture/
).

The update history is stored on all nodes through a Blockchain whose consensus protocol used is [Raft](https://raft.github.io/raft.pdf).

The update files pointed to by the history are distributed by the nodes through a distributed hash table (DHT) with the [Kademlia](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf) algorithm.

### RAFT

Fault-tolerant consensus protocol in which all nodes run the same state machine.

#### General Features

* Nodes can assume the roles of followers, candidates, or leader.
* The network will always elect a leader through an election of candidates who will be responsible for replicating the data in the other nodes called followers. 
* All RPCs are invoked either by leaders or candidates, never by followers.
* Prioritizes consistency over availability, thus the system is only available when a leader has been elected and is alive. Otherwise, a new leader will be elected and the system will remain unavailable during the vote.
* The client interacts with the network only through the leader, an alternative is for the follower to act as a proxy and forward the client's requests to the leader.
* All messages exchanged between nodes have the mandate number (term).
* In case of failure of the leader the other nodes initiate an election to determine the new leader.

#### Election

* All nodes are initially followers and after a random time without receiving a heartbeat from leader they start the election process as candidates. The random and consequently different time at each node means that normally only one of the nodes in the network initiates a election process as a candidate.
* The candidate votes for himself (votedFor), increases the term number (currentTerm) and requests the other nodes in the network to vote. If it receives votes from more than half of the nodes in the network, this node assumes that it is the new leader.
* A node votes for a candidate only if the candidate's term number is greater than the current term number and if he has not already voted in this election and if the candidate’s log is as up to date as the follower.
* An election can end without a winner, in this case the candidates and the other nodes again wait for a random time and a new election is initiated.
* When a candidate or leader receives a message with a term higher than your, he becomes a follower.
* The leader, in the case of network idleness, sends heartbeats to the other nodes in order to prevent unnecessary elections.
* The leader, when elected, initializes each follower's nextIndex with his lastLogIndex + 1.

#### Replication

* The leader when receiving an entry from the client attached to his local log and initiates the process of replicating this entry in the followers. The log is considered committed (commitIndex) when more than half of the nodes in the network confirm its replication. Followers understand that a log has been committed when the leader announces the last index committed to their RPC's. The client obtains the result of the entry only when it is committed by leader.
* Followers reject leader entries with a lower mandate (term) number than practiced.
* It is stored by the leader, for each follower, the index of the next log (nextIndex) to be sent and the index of the last log replicated by the follower (matchIndex).
* If the follower finds that the immediately previous log (prevLogIndex and prevLogTerm) sent by the leader does not match its local log it will refuse the entries. In this case the leader will reduce the nextIndex until he accepts the entries, that is, until the last entry accepted by the follower is discovered. An alternative that can be used to speed up this process is the follower when refusing the entries inform the leader the index of the last entry present in his log.
* All entries that are not yet in the log are added by the followers, but if an inconsistency is detected in the new entries (same index, but for different mandates), the follower deletes the entries from this index onwards and assumes the entries of the current leader.
* If the leader's commit index (leaderCommitIndex) is higher than follower (commitIndex) the follower new commitIndex will be equal to min (leaderCommitIndex, index of the new entry) 

### API

Documentation for integration with the nodes is available at [API](https://github.com/CleberPeter/dOTA/blob/main/docs/api.md). 

### Blockchain

The structure employed for each of the blockchain blocks is available at [Blockchain](https://github.com/CleberPeter/dOTA/blob/main/docs/blockchain_blocks.md).
