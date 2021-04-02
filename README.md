# dOTA

A distributed and fault-tolerant approach to the Over-The-Air (OTA) upgrade of embedded systems in compliance with the Internet Engineering Task Force (IETF) Secure Update Internet of Things [(SUIT)](https://datatracker.ietf.org/doc/draft-ietf-suit-architecture/
).

The update history is stored on all nodes through a Blockchain whose consensus protocol used is [raft](https://raft.github.io/raft.pdf)
.

The update files pointed to by the history are distributed by the nodes through a distributed hash table (DHT) with the [kademlia](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf) algorithm.


# REST API

Used for interaction with nodes

```console
root@pc:~$ curl -X POST localhost:8080 -d 'action=kill'
```
