from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorirendezvous.client.structs.protocol import ToServerProtocol
from satorirendezvous.server.behaviors.connect import ClientConnect as BaseClientConnect
from satorirendezvous.server.structs.message import ToServerMessage
from satorirendezvous.server.structs.protocol import ToClientProtocol
from satorirendezvous.server.structs.client import RendezvousClient
logging.setup(file='/tmp/rendezvous.log')


class ClientConnect(BaseClientConnect):

    # override
    def respond(self, msgId: str, msg: str):
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

    ### routing messages ###

    # override
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
    def _handleCheckIn(self, msg: ToServerMessage):
        ''' CHECKIN|msgId '''
        if not self._authenticationHook(msg):
            return False
        rendezvousClient = RendezvousClient(
            address=msg.address,
            ip=msg.ip,
            port=msg.port)
        with self.clients:
            self.clients.append(rendezvousClient)
        return self.respond(
            msgId=msg.msgId,
            msg='welcome to the Satori Rendezvous Server'), rendezvousClient

    # override
    def _handlePorts(self, rendezvousClient: RendezvousClient):
        ''' PORTS|msgId|portsTaken '''
        rendezvousClient.portsTaken = TwoWayDictionary.fromDict({
            **rendezvousClient.portsTaken,
            **rendezvousClient.msg.portsTaken})
        return self.respond(
            msgId=rendezvousClient.msg.msgId,
            msg='ports received')

    # override
    def _handleBeat(self, rendezvousClient: RendezvousClient):
        ''' BEAT|msgId '''
        # there is no real need to respond - we just send 3 per 5 minutes
        # anyway in case there is the occasional lost packet. however, the
        # client will skip 1 beat if it receives a beat from the server.
        return self.respond(
            msgId=rendezvousClient.msg.msgId,
            msg='beat')

    # override
    def router(self, data: bytes, address: tuple[str, int]):
        ''' routes all messages to the appropriate handler '''
        msg = ToServerMessage.fromBytes(data, *address)
        if msg.isCheckIn():
            rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
            resonse = None
            if rendezvousClient is None:
                resonse, rendezvousClient = self._handleCheckIn(msg)
            else:
                rendezvousClient.addMsg(msg)
            if self.fullyConnected:
                return self._handleConnectToAll(rendezvousClient)
            else:
                # that's not part of the protocol
                return resonse or str(rendezvousClient)
        else:
            rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
            if rendezvousClient is None:
                return self.respond(
                    msgId=msg.msgId,
                    msg='client not found: please checkin again.')
            else:
                rendezvousClient.addMsg(msg)
                if msg.isPortsTaken():
                    return self._handlePorts(rendezvousClient)
                elif msg.isBeat():
                    return self._handleBeat(rendezvousClient)
                return self.routeMessage(msg, rendezvousClient)

    def aClientConnection(
        self,
        topic: str,
        clientA: RendezvousClient,
        clientB: RendezvousClient,
    ):
        return self.notifyClientOfPeer(topic, clientA, clientB)
