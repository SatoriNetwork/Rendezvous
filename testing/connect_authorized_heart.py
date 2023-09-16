'''
raw connection ability - without any authorization
this one has a heart beat so we can see when it looses connection.
we discovered we loose connection to the client when the server has not sent the
client anything and the client hasn't sent us anything for exactly 5 minutes. 
However, the client can send a message to the server at anytime and doesn't need
to re-establish a connection. not sure why. So the clients will all heart beat
the server every 4.9 minutes to keep the connection alive. and they'll heart 
beat each other at random intervals every 4.9 minutes to keep their p2p
connections alive. no need for clients or server to respond, apparently.
'''

import time
import threading
from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorilib.api.udp.rendezvous import UDPRendezvousMessage
from satorirendezvous.server.structs.client import RendezvousClient
logging.setup(file='/tmp/rendezvous.log')


class ConnectAuthorizedHeartBehavior():

    def __init__(self):
        logging.info('starting rendezvous server...')
        self.clients: list[RendezvousClient] = []
        self.clientsBySubscription: dict[str, list[RendezvousClient]] = {}

    def process(self):
        def _handleCheckIn(msg: UDPRendezvousMessage):
            ''' CHECKIN|msgId '''

            def _setupHeartBeat(msg: UDPRendezvousMessage):

                def _heartbeat():
                    beats = 295
                    while True:
                        self.respond(
                            address=msg.address,
                            msgId=msg.msgId,
                            msg=f'BEAT|{beats}')
                        # beats = int(beats * 1.6182)
                        # beats = int(beats * 2)
                        beats += 1
                        time.sleep(beats)

                listener = threading.Thread(target=_heartbeat, daemon=True)
                listener.start()

            rendezvousClient = RendezvousClient(
                address=msg.address,
                ip=msg.ip,
                port=msg.port)
            self.clients.append(rendezvousClient)
            self.respond(
                address=msg.address,
                msgId=msg.msgId,
                msg='welcome to the Satori Rendezvous Server')
            _setupHeartBeat(msg)

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
            decryptedKey = rendezvousClient.msg.key
            # this subscriptions should be a list of strings, I think it
            # decryptedKey.subscriptions should include all the streams
            # because I think we subscribe to all streams that we publish
            # as well. but we'll use decryptedKey.streams because it
            # combines the two sets anyway.
            subscriptions = decryptedKey.streams()
            for subscription in subscriptions:
                # connect everyone to the new client
                # - assign the client a port number for this topic
                # -- get a list of all ports not taken for that topic
                # -- get an available port from that list for the client
                peers = self.clientsBySubscription[subscription]
                self.clientsBySubscription[subscription] = rendezvousClient
                portsTaken = {peer.portFor(subscription) for peer in peers}
                availablePorts = self.portRange - portsTaken
                chosenPort = rendezvousClient.randomAvailablePort(
                    availablePorts)
                rendezvousClient.portsAssigned[subscription] = chosenPort
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

        def _handleBeat(rendezvousClient: RendezvousClient):
            ''' BEAT|msgId '''
            self.respond(
                address=rendezvousClient.msg.address,
                msgId=rendezvousClient.msg.msgId,
                msg='beat received')

        def _manageFindClient(msg: UDPRendezvousMessage):
            ''' finds client and attaches message to it's list of msgs '''
            rendezvousClient = self.findClient(ip=msg.ip, port=msg.port)
            if rendezvousClient is None:
                return None
            rendezvousClient.addMsg(msg)
            return rendezvousClient

        logging.info('starting rendezvous worker...')
        while True:
            data, address = self.queue.get()
            logging.info(f'connection from: {address} with: {data}')
            msg = UDPRendezvousMessage.fromBytes(data, *address)
            if msg.isCheckIn():
                _handleCheckIn(msg)
            else:
                rendezvousClient = _manageFindClient(msg)
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
            f'{clientB.ip} {clientB.portFor(topic)} '
            f'{topic} {clientA.portFor(topic)}').encode(),
            clientA.address)
        self.sock.sendto((
            f'{clientA.ip} {clientA.portFor(topic)} '
            f'{topic} {clientB.portFor(topic)}').encode(),
            clientB.address)
