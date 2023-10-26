import time
from satorilib import logging
from satorirendezvous.server.rest.behaviors.connect import ClientConnect
from satorirendezvous.server.structs.client import RendezvousClient
from satorirendezvous.example.server.structs.client import RendezvousClientsBySubscription
from satorirendezvous.example.server.structs.message import ToServerSubscribeMessage
from satorirendezvous.server.structs.protocol import ToClientProtocol


class SubscribingClientConnect(ClientConnect):
    ''' add the ability to subscribe to topics to the server '''

    def __init__(self):
        super().__init__(fullyConnected=False)
        self.clientsBySubscription: RendezvousClientsBySubscription = (
            RendezvousClientsBySubscription({}))

    # override
    def purge(self):
        while True:
            lastPurge = time.time()
            time.sleep(60*60*24)
            with self.clients:
                self.clients = [
                    client for client in self.clients
                    if client.lastSeen > lastPurge]
            with self.clientsBySubscription:
                self.clientsBySubscription = {
                    k: [client for client in v if client.lastSeen > lastPurge]
                    for k, v in self.clientsBySubscription.items()}

    # override
    def routeMessage(
        self,
        msg: ToServerSubscribeMessage,
        rendezvousClient: RendezvousClient,
    ):
        ''' route for subscription messages '''
        if msg.isSubscribe():
            return self._handleSubscribe(rendezvousClient)
        return self.postRouteMessage(msg, rendezvousClient)

    def postRouteMessage(
        self,
        msg: ToServerSubscribeMessage,  # keep
        rendezvousClient: RendezvousClient,  # keep
    ):
        ''' post route hook '''
        return 'postRouteMessage not implemented'

    def preSubscriptionHook(self, rendezvousClient: RendezvousClient):
        ''' pre subscription hook '''
        rendezvousClient.seen()

    # fix this - needs to return a list of peers to connect to.
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
        if key is None:
            return
        self.preSubscriptionHook(rendezvousClient)
        if isinstance(key, str):
            subscriptions = key.split('|')
        else:
            # assume a type that contains streams() prop
            subscriptions = key.streams()
        for subscription in subscriptions:
            # connect everyone to the new client
            # - assign the client a port number for this topic
            # -- get a list of all ports not taken for that topic
            # -- get an available port from that list for the client
            peers = [
                peer for peer in self.clientsBySubscription.get(
                    subscription) or []
                if peer.lastSeen > time.time()-60*60*24]
            if rendezvousClient not in peers:
                portsTaken = {peer.portFor(subscription) for peer in peers}
                availablePorts = self.portRange - portsTaken
                chosenPort = rendezvousClient.randomAvailablePort(
                    availablePorts)
                rendezvousClient.portsAssigned[subscription] = chosenPort
                peers.append(rendezvousClient)
            self.clientsBySubscription[subscription] = peers
            # if this connection process takes too long it should be
            # moved to a thread. actually we should just move all this
            # to a stream and use rx like the node does, but we'll do
            # that later.
            return [self._connectClientsTogether(
                topic=subscription,
                client=rendezvousClient,
                peer=peer)
                for peer in peers
                if peer != rendezvousClient]
        logging.debug('self.clientsBySubscription')
        logging.debug(self.clientsBySubscription)

    def _connectClientsTogether(
        self,
        topic: str,
        client: RendezvousClient,
        peer: RendezvousClient,
    ) -> str:
        ''' connects the two clients '''
        return self._notifyClientOfPeer(
            topic=topic,
            client=client,
            peer=peer)
        # if peer.lastSeen > time.time()-60*60*5:
        #    self._notifyClientOfPeer(
        #        topic=topic,
        #        clientA=peer,
        #        clientB=client)

    # fix this - needs to return a list of peers to connect to.
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
        return ToClientProtocol.compile(
            ToClientProtocol.connectPrefix,
            topic, peer.ip, peer.portFor(topic), client.portFor(topic))
