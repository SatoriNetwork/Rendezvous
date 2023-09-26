import json
import time
from satorirendezvous.example.client.structs.protocol import ToServerSubscribeProtocol
from satorirendezvous.peer.peer.rest import Peer


class SubscribingPeer(Peer):
    ''' manages connection to the rendezvous server and all our udp topics '''

    def __init__(
        self,
        rendezvousHost: str,
        topics: list[str] = None,
        handlePeriodicCheckin: bool = True,
        periodicCheckinSeconds: int = 60*60*1,
    ):
        super().__init__(
            rendezvousHost=rendezvousHost,
            topics=topics,
            handlePeriodicCheckin=handlePeriodicCheckin,
            periodicCheckinSeconds=periodicCheckinSeconds)

    # override
    def checkin(self):
        while True:
            for topic in self.topics.keys():
                time.sleep(self.periodicCheckinSeconds)
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
