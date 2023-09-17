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

    def __init__(self):
        logging.info('starting rendezvous server...')
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
        self.sock.sendto((
            f'CONNECTION|{topic}|{clientB.ip}|{clientB.portFor(topic)}|'
            f'{clientA.portFor(topic)}').encode(),
            clientA.address)
        self.sock.sendto((
            f'CONNECTION|{topic}|{clientA.ip}|{clientA.portFor(topic)}|'
            f'{clientB.portFor(topic)}').encode(),
            clientB.address)

    ### routing messages ###

    def _handleCheckIn(self, msg: ToServerMessage):
        ''' CHECKIN|msgId '''
        rendezvousClient = RendezvousClient(
            address=msg.address,
            ip=msg.ip,
            port=msg.port)
        self.clients.append(rendezvousClient)
        self.respond(
            address=msg.address,
            msgId=msg.msgId,
            msg='welcome to the Satori Rendezvous Server')

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
        msg: ToServerMessage,
        rendezvousClient: RendezvousClient,
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
                self._handleCheckIn(msg)
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
