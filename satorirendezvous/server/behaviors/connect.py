import socket
import queue
from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorirendezvous.server.structs.message import ToServerMessage
from satorirendezvous.server.structs.client import RendezvousClient
logging.setup(file='/tmp/rendezvous.log')


class ClientConnect():
    ''' 
    a set of behaviors the server performs when a client connects and sends
    messages to it. remembers clients and the ports they used to connect clients
    to each other. will connect clients to each other based upon the topics they
    subscribe to. raw connection ability - without any authorization. (todo: 
    break this up into smaller behaviors...)
    '''

    def __init__(self, fullyConnected: bool = False):
        logging.info('starting rendezvous server...')
        # if fullyConnected is True, then all clients will connect to all
        # clients which is non-typical as it only works for small networks.
        self.fullyConnected = fullyConnected
        self.portRange: set[int] = set(range(49153, 65536))
        self.clients: list[RendezvousClient] = []

    def setSockQueue(self, sock: socket.socket, queue: queue.Queue):
        ''' must set the sock and queue before calling router '''
        self.sock = sock
        self.queue = queue

    ### finding client ###

    def findClient(self, ip: str, port: int):
        try:
            return [
                client for client in self.clients
                if client.ip == ip and port == port][0]
        except Exception as e:
            logging.error((
                'unable to find client for ports, they did not checkin '
                'first... they are not a client.'),
                e)
            return None

    ### using socket ###

    def respond(self, address: tuple[str, int], msgId: str, msg: str):
        logging.debug('responding to:', address, f'{msgId}|{msg}')
        self.sock.sendto(f'{msgId}|{msg}'.encode(), address)

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
        self.sock.sendto((
            f'CONNECTION|{topic}|{peer.ip}|{peer.portFor(topic)}|'
            f'{client.portFor(topic)}').encode(),
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
        return True

    def _getKey(self, msg: ToServerMessage) -> str:
        ''' get key of message hook '''
        return msg.key

    ### connecting clients together ###

    def _handleConnectToAll(
        self,
        rendezvousClient: RendezvousClient,
    ):
        topic = 'fullyConnected'
        clients = [client for client in self.clients if client !=
                   rendezvousClient]
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
        logging.debug('_handleBeat')
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

        pass

    def router(self):
        ''' routes all messages to the appropriate handler '''
        logging.info('starting rendezvous worker...')
        while True:
            data, address = self.queue.get()
            logging.debug(f'connection from: {address} with: {data}')
            msg = ToServerMessage.fromBytes(data, *address)
            if msg.isCheckIn():
                rendezvousClient = self._handleCheckIn(msg)
                if self.fullyConnected:
                    self._handleConnectToAll(rendezvousClient)
            else:
                logging.debug('else')
                rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
                logging.debug('client:', rendezvousClient)
                logging.debug('msgtype:', msg.isPortsTaken(),
                              msg.isSubscribe(), msg.isBeat())
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
