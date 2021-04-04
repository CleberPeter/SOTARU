# dOTA

A distributed and fault-tolerant approach to the Over-The-Air (OTA) upgrade of embedded systems in compliance with the Internet Engineering Task Force (IETF) Secure Update Internet of Things [(SUIT)](https://datatracker.ietf.org/doc/draft-ietf-suit-architecture/
).

The update history is stored on all nodes through a Blockchain whose consensus protocol used is [Raft](https://raft.github.io/raft.pdf).

The update files pointed to by the history are distributed by the nodes through a distributed hash table (DHT) with the [Kademlia](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf) algorithm.

### HTTP API

Documentation for integration with the nodes is available at [HTTP_API](https://github.com/CleberPeter/dOTA/blob/main/docs/api.md). 

### Blockchain Blocks

The structure employed for each of the blockchain blocks is available at [Blockchain_blocks](https://github.com/CleberPeter/dOTA/blob/main/docs/blockchain_blocks.md).