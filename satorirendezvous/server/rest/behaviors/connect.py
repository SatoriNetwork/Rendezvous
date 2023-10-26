from satorilib import logging
from satorirendezvous.client.structs.protocol import ToServerProtocol
from satorirendezvous.server.behaviors.connect import ClientConnect as BaseClientConnect
from satorirendezvous.server.structs.message import ToServerMessage
from satorirendezvous.server.structs.protocol import ToClientProtocol
from satorirendezvous.server.structs.client import RendezvousClient
logging.setup(file='/tmp/rendezvous.log')


class ClientConnect(BaseClientConnect):

    # override
    def respond(self, address: tuple[str, int], msgId: str, msg: str):
        ''' f'RESPONSE|{msgId}|{msg}' '''
        return ToClientProtocol.compile(
            ToClientProtocol.responsePrefix,
            msgId,
            msg)

    # override
    def notifyClientOfPeer(
        self,
        topic: str,
        client: RendezvousClient,
        peer: RendezvousClient,
    ):
        '''
        tells client the peer's address and port, the topic, and which port to
        use for that topic.
        '''
        return ToClientProtocol.compile(
            ToClientProtocol.connectPrefix,
            topic, peer.ip, peer.portFor(topic), client.portFor(topic))

    def aClientConnection(
        self,
        topic: str,
        clientA: RendezvousClient,
        clientB: RendezvousClient,
    ):
        return self.notifyClientOfPeer(topic, clientA, clientB)

    def _handleConnectToAll(self, rendezvousClient: RendezvousClient):
        topic = ToServerProtocol.fullyConnectedKeyword
        clients = [
            client for client in self.clients
            if client != rendezvousClient]
        portsTaken = {client.portFor(topic) for client in clients}
        availablePorts = self.portRange - portsTaken
        chosenPort = rendezvousClient.randomAvailablePort(availablePorts)
        rendezvousClient.portsAssigned[topic] = chosenPort
        return [
            ToClientProtocol.compile(
                ToClientProtocol.connectPrefix, topic, peer.ip,
                peer.portFor(topic), rendezvousClient.portFor(topic))
            for peer in clients]

    # override

    def router(self, data: bytes, address: tuple[str, int]):
        ''' routes all messages to the appropriate handler '''
        logging.info('starting rendezvous worker...')
        msg = ToServerMessage.fromBytes(data, *address)
        if msg.isCheckIn():
            rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
            if rendezvousClient is None:
                rendezvousClient = self._handleCheckIn(msg)
            else:
                rendezvousClient.addMsg(msg)
            if self.fullyConnected:
                return self._handleConnectToAll(rendezvousClient)
            else:
                return str(rendezvousClient)
        else:
            rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
            if rendezvousClient is None:
                return self.respond(
                    address=msg.address,
                    msgId=msg.msgId,
                    msg='client not found: please checkin again.')
            else:
                rendezvousClient.addMsg(msg)
                if msg.isPortsTaken():
                    return self._handlePorts(rendezvousClient)
                elif msg.isBeat():
                    return self._handleBeat(rendezvousClient)
                return self.routeMessage(msg, rendezvousClient)
