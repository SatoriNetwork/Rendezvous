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
        self.clientsBySubscription: dict[str, list[RendezvousClient]] = {}

    def process(self):
        def _handleCheckIn(msg: ToServerMessage):
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

        def _handlePorts(rendezvousClient: RendezvousClient):
            ''' PORTS|msgId|portsTaken '''
            rendezvousClient.portsTaken = TwoWayDictionary.fromDict({
                **rendezvousClient.portsTaken,
                **rendezvousClient.msg.portsTaken})
            self.respond(
                address=rendezvousClient.msg.address,
                msgId=rendezvousClient.msg.msgId,
                msg='ports received')

        def _handleSubscribe(rendezvousClient: RendezvousClient):
            ''' SUBSCRIBE|msgId|signature|key '''
            logging.debug('_handleSubscribe')
            logging.debug('rendezvousClient.msg', rendezvousClient.msg)
            logging.debug('rendezvousClient.msg.key', rendezvousClient.msg.key)
            key = rendezvousClient.msg.key
            # this subscriptions should be a list of strings, I think it
            # decryptedKey.subscriptions should include all the streams
            # because I think we subscribe to all streams that we publish
            # as well. but we'll use decryptedKey.streams because it
            # combines the two sets anyway.
            subscriptions = key.streams()
            logging.debug('subscriptions:', subscriptions)
            for subscription in subscriptions:
                # connect everyone to the new client
                # - assign the client a port number for this topic
                # -- get a list of all ports not taken for that topic
                # -- get an available port from that list for the client
                logging.debug('subscription:', subscription)
                peers = self.clientsBySubscription.get(subscription) or []
                logging.debug('peers:', peers)
                if len(peers) == 0:
                    self.clientsBySubscription[subscription] = [
                        rendezvousClient]
                else:
                    self.clientsBySubscription[subscription].append(
                        rendezvousClient)
                logging.debug('self.clientsBySubscription1:',
                              self.clientsBySubscription)
                portsTaken = {peer.portFor(subscription) for peer in peers}
                logging.debug('portsTaken:', portsTaken)
                availablePorts = self.portRange - portsTaken
                logging.debug('availablePorts:', len(availablePorts))
                chosenPort = rendezvousClient.randomAvailablePort(
                    availablePorts)
                logging.debug('chosenPort:', chosenPort)
                rendezvousClient.portsAssigned[subscription] = chosenPort
                logging.debug('rendezvousClient:',
                              rendezvousClient.portsAssigned)
                # if this connection process takes too long it should be
                # moved to a thread. actually we should just move all this
                # to a stream and use rx like the node does, but we'll do
                # that later.
                for peer in peers:
                    if peer != rendezvousClient:
                        self.connectTwoClients(
                            topic=subscription,
                            clientA=rendezvousClient,
                            clientB=peer)
            logging.debug('self.clientsBySubscription')
            logging.debug(self.clientsBySubscription)

        def _handleBeat(rendezvousClient: RendezvousClient):
            ''' BEAT|msgId '''
            # there is no real need to respond - we just send 3 per 5 minutes
            # anyway in case there is the occasional lost packet. however, the
            # client will skip 1 beat if it receives a beat from the server.
            logging.debug('_handleBeat')
            self.respond(
                address=rendezvousClient.msg.address,
                msgId=rendezvousClient.msg.msgId,
                msg='beat')

        def _manageFindClient(msg: ToServerMessage):
            ''' finds client and attaches message to it's list of msgs '''
            rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
            if rendezvousClient is None:
                return None
            rendezvousClient.addMsg(msg)
            return rendezvousClient

        logging.info('starting rendezvous worker...')
        while True:
            data, address = self.queue.get()
            logging.debug(f'connection from: {address} with: {data}')
            msg = ToServerMessage.fromBytes(data, *address)
            if msg.isCheckIn():
                _handleCheckIn(msg)
            else:
                logging.debug('else')
                rendezvousClient = _manageFindClient(msg)
                logging.debug('client:', rendezvousClient)
                logging.debug('msgtype:', msg.isPortsTaken(),
                              msg.isSubscribe(), msg.isBeat())
                if rendezvousClient is None:
                    self.respond(
                        address=msg.address,
                        msgId=msg.msgId,
                        msg='client not found: please checkin again.')
                elif msg.isPortsTaken():
                    _handlePorts(rendezvousClient)
                elif msg.isSubscribe():
                    _handleSubscribe(rendezvousClient)
                elif msg.isBeat():
                    _handleBeat(rendezvousClient)
            self.queue.task_done()

    def findClient(self, ip: str, port: int):
        try:
            return [
                client for client in self.clients
                if client.ip == ip and port == port][0]
        except Exception as e:
            logging.error((
                'unable to find client for ports, they did not checkin '
                'first... they are not a node.'),
                e)
            return None

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
