# Rendezvous
Satori Rendezvous server and peers functionalty.

Uses UDP hole punching to establish a UDP p2p mesh network without the need to open ports on personal firewalls.

## benefits

In most cases peers do not need to modify their firewalls. NATs don't seem to cause an issue in most cases and this has even been tested over VPNs. It seems to be one of the simplest, yet most robust methods of p2p communication.

## conceptual requirements

This requires a centralized server to work. it's a rendezvous server, clients connect and the server provides them with information required to connect to their peers.

Each peer must maintain an active connection to the server. This way when new peers connect, the existing peers on the network can learn about them and connect to them directly.

## ideal usecase

The Satori Network (satorinet.io) developed this method for p2p communication in order to incrementally share large amounts of data directly between Satori Neurons.

## use
```
from Rendezvous import Server, ToServerProtocol, ToPeerProtocol, PeerProtocol

Class MyProtocol(ToServerProtocol, ToPeerProtocol):
    #...@overrides...
    #...and additions...
    @staticmethod
    def additionalCommand() -> bytes:
        return b'COMMAND'
        
Class MyServer(Server):
    #...@overrides...
    #...and additions...
    @staticmethod
    def additionalCommand() -> bytes:
        return respond('GRANTED') 

# on server machine:
server = MyServer(protocol: MyProtocol)
server.run()

# on machine A:
peerA = Peer(
    serverProtocol: MyProtocol,
    peerToServerProtocol: MyProtocol,
    peerToPeerProtocol: PeerProtocol,
    serverAddress: '192.168.0.1')
peerA.run()
# > conecting to rendezvous server...
# > conected to rendezvous server...
# > discovered peer 192.168.0.3...
# > conecting to peer 192.168.0.3...
# > conected to peer 192.168.0.3...
# > peer request: '...'...
# > response: '...'...

# on machine B:
peerB = Peer(
    serverProtocol: MyProtocol,
    peerToServerProtocol: MyProtocol,
    peerToPeerProtocol: PeerProtocol,
    serverAddress: '192.168.0.1')
peerB.run()
# > conecting to rendezvous server...
# > conected to rendezvous server...
# > discovered peer 192.168.0.2...
# > conecting to peer 192.168.0.2...
# > conected to peer 192.168.0.2...
# > peer request: '...'...
# > response: '...'...

```