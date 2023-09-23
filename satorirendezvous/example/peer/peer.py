import json
import time
from satorirendezvous.example.client.structs.protocol import ToServerSubscribeProtocol
from satorirendezvous.peer.peer import Peer

# todo: update example stuff
# this version should just be subscribing, we should do authentication in our
# project


class SubscribingPeer(Peer):
    ''' manages connection to the rendezvous server and all our udp topics '''

    def __init__(
        self,
        rendezvousHost: str,
        rendezvousPort: int,
        topics: list[str] = None,
        handlePeriodicCheckin: bool = True,
        periodicCheckinSeconds: int = 60*60*1,
    ):
        super().__init__(
            rendezvousHost=rendezvousHost,
            rendezvousPort=rendezvousPort,
            topics=topics,
            handlePeriodicCheckin=handlePeriodicCheckin,
            periodicCheckinSeconds=periodicCheckinSeconds)

    # override
    def checkin(self):
        while True:
            for topic in self.topics.keys():
                time.sleep(self.periodicCheckinSeconds)
                self.rendezvous.establish()
                # todo: do we have to fully establish a connetion or just send
                # a checkin message? well we have to establish a new listener
                # anyway
                self.sendTopic(topic)

    def sendTopics(self):
        ''' send our topics to the rendezvous server to get peer lists '''
        for topic in self.topics.keys():
            self.sendTopic(topic)

    def sendTopic(self, topic: str):
        self.rendezvous.send(
            cmd=ToServerSubscribeProtocol.subscribePrefix,
            msgs=[
                json.dumps({
                    **{'pubkey': 'wallet.pubkey'},
                    **(
                        {
                            'publisher': [topic]}
                    ),
                    **(
                        {
                            'subscriptions': [topic]
                        }
                    )})])
