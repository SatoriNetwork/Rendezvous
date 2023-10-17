import time
import socket
import queue
import threading
from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorirendezvous.client.structs.protocol import ToServerProtocol
from satorirendezvous.server.structs.protocol import ToClientProtocol
from satorirendezvous.server.structs.message import ToServerMessage
from satorirendezvous.server.structs.client import RendezvousClient, RendezvousClients
logging.setup(file='/tmp/rendezvous.log')


class ClientConnect():
    ''' 
    a set of behaviors the server performs when a client connects and sends
    messages to it. remembers clients and the ports they used to connect clients
    to each other. will connect clients to each other based upon the topics they
    subscribe to. raw connection ability - without any authorization. (todo: 
    break this up into smaller behaviors...)
    '''

    def __init__(self, fullyConnected: bool = True):
        logging.info('starting rendezvous server...')
        # if fullyConnected is True, then all clients will connect to all
        # clients which is non-typical as it only works for small networks.
        # however, it is the default because without any higher layers we have
        # no way of knowing who should be connected to who.
        self.fullyConnected = fullyConnected
        self.portRange: set[int] = set(range(49153, 65536))
        self.clients: RendezvousClients = RendezvousClients([])
        self.periodicPurge()

    def periodicPurge(self):
        self.purger = threading.Thread(target=self.purge, daemon=True)
        self.purger.start()

    def purge(self):
        while True:
            lastPurge = time.time()
            time.sleep(60*60*24)
            with self.clients:
                self.clients = [
                    client for client in self.clients
                    if client.lastSeen > lastPurge]

    def setSock(self, sock: socket.socket):
        ''' must set the sock and queue before calling router '''
        self.sock = sock

    def setQueue(self, queue: queue.Queue):
        ''' must set the sock and queue before calling router '''
        self.queue = queue

    ### finding client ###

    def findClient(self, ip: str, port: int):
        try:
            clients = [
                client for client in self.clients
                if client.ip == ip and port == port]
            if len(clients) > 0:
                return clients[0]
        except Exception as e:
            logging.error((
                'unable to find client for ports, they did not checkin '
                'first... they are not a client.'),
                e)
        return None

    ### using socket ###

    def respond(self, address: tuple[str, int], msgId: str, msg: str):
        ''' f'RESPONSE|{msgId}|{msg}' '''
        self.sock.sendto(
            ToClientProtocol.compile(
                ToClientProtocol.responsePrefix,
                msgId,
                msg),
            address)

    def _notifyClientOfPeer(
        self,
        topic: str,
        client: RendezvousClient,
        peer: RendezvousClient,
    ):
        '''
        tells client the peer's address and port, the topic, and which port to
        use for that topic.
        '''
        self.sock.sendto(
            ToClientProtocol.compile(
                ToClientProtocol.connectPrefix,
                topic, peer.ip, peer.portFor(topic), client.portFor(topic)),
            client.address)

    def connectTwoClients(
        self,
        topic: str,
        clientA: RendezvousClient,
        clientB: RendezvousClient,
    ):
        '''
        tells them each other's address and port, the topic, and which port to
        use for that topic.
        '''
        self._notifyClientOfPeer(topic, clientA, clientB)
        self._notifyClientOfPeer(topic, clientB, clientA)

    ### authentication hooks ###

    def _authenticationHook(self, msg: ToServerMessage) -> bool:
        ''' authentication hook '''
        logging.debug('auth hook!', print='teal')
        return True

    def _getKey(self, msg: ToServerMessage) -> str:
        ''' get key of message hook '''
        return msg.key

    ### connecting clients together ###

    def _handleConnectToAll(self, rendezvousClient: RendezvousClient):
        topic = ToServerProtocol.fullyConnectedKeyword
        clients = [
            client for client in self.clients
            if client != rendezvousClient]
        portsTaken = {client.portFor(topic) for client in clients}
        availablePorts = self.portRange - portsTaken
        chosenPort = rendezvousClient.randomAvailablePort(availablePorts)
        rendezvousClient.portsAssigned[topic] = chosenPort
        for client in clients:
            self.connectTwoClients(
                topic=topic,
                clientA=rendezvousClient,
                clientB=client)

    ### routing messages ###

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
        self.respond(
            address=msg.address,
            msgId=msg.msgId,
            msg='welcome to the Satori Rendezvous Server')
        return rendezvousClient

    def _handlePorts(self, rendezvousClient: RendezvousClient):
        ''' PORTS|msgId|portsTaken '''
        rendezvousClient.portsTaken = TwoWayDictionary.fromDict({
            **rendezvousClient.portsTaken,
            **rendezvousClient.msg.portsTaken})
        self.respond(
            address=rendezvousClient.msg.address,
            msgId=rendezvousClient.msg.msgId,
            msg='ports received')

    def _handleBeat(self, rendezvousClient: RendezvousClient):
        ''' BEAT|msgId '''
        # there is no real need to respond - we just send 3 per 5 minutes
        # anyway in case there is the occasional lost packet. however, the
        # client will skip 1 beat if it receives a beat from the server.
        self.respond(
            address=rendezvousClient.msg.address,
            msgId=rendezvousClient.msg.msgId,
            msg='beat')

    def routeMessage(
        self,
        msg: ToServerMessage,  # keep
        rendezvousClient: RendezvousClient,  # keep
    ):
        ''' this is meant to be overridden if custom behavior is added '''
        return f'unable to route message {str(msg)}, {str(rendezvousClient)}'

    def router(self):
        ''' routes all messages to the appropriate handler '''
        logging.info('starting rendezvous worker...')
        while True:
            data, address = self.queue.get()
            msg = ToServerMessage.fromBytes(data, *address)
            if msg.isCheckIn():
                rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
                if rendezvousClient is None:
                    rendezvousClient = self._handleCheckIn(msg)
                else:
                    rendezvousClient.addMsg(msg)
                if self.fullyConnected:
                    self._handleConnectToAll(rendezvousClient)
            else:
                rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
                if rendezvousClient is None:
                    self.respond(
                        address=msg.address,
                        msgId=msg.msgId,
                        msg='client not found: please checkin again.')
                else:
                    rendezvousClient.addMsg(msg)
                    if msg.isPortsTaken():
                        self._handlePorts(rendezvousClient)
                    elif msg.isBeat():
                        self._handleBeat(rendezvousClient)
                    else:
                        self.routeMessage(msg, rendezvousClient)
            self.queue.task_done()
