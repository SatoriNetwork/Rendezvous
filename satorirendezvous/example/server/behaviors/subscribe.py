from satorilib import logging
from satorirendezvous.server.behaviors.simple_connect import ClientConnect
from satorirendezvous.server.structs.client import RendezvousClient
from satorirendezvous.server.structs.message import ToServerMessage


class SubscribingClientConnect(ClientConnect):
    ''' add the ability to subscribe to topics to the server '''

    def __init__(self):
        super().__init__()
        self.clientsBySubscription: dict[str, list[RendezvousClient]] = {}

    # override
    def routeMessage(
        self,
        msg: ToServerMessage,
        rendezvousClient: RendezvousClient,
    ):
        ''' route for subscription messages '''
        if msg.isSubscribe():
            self._handleSubscribe(rendezvousClient)
        self.postRouteMessage(msg, rendezvousClient)

    def postRouteMessage(
        self,
        msg: ToServerMessage,
        rendezvousClient: RendezvousClient,
    ):
        ''' post route hook '''
        pass

    def _handleSubscribe(self, rendezvousClient: RendezvousClient):
        ''' SUBSCRIBE|msgId|signature|key '''
        logging.debug('_handleSubscribe')
        logging.debug('rendezvousClient.msg', rendezvousClient.msg)
        logging.debug('rendezvousClient.msg.key', rendezvousClient.msg.key)
        key = self._getKey(rendezvousClient.msg)
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
