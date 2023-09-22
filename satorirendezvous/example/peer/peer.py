import json
from satorirendezvous.example.client.structs.protocol import ToServerSubscribeProtocol
from satorirendezvous.example.client.connect import RendezvousAuthenticatedConnection
from satorirendezvous.peer.peer import Peer


class AuthenticatedSubscribingPeer(Peer):
    ''' manages connection to the rendezvous server and all our udp topics '''

    def __init__(
        self,
        rendezvousHost: str,
        rendezvousPort: int,
        topics: list[str] = None,
        signature: str = None,
        key: str = None,
    ):
        self.signature = signature
        self.key = key
        super().__init__(
            rendezvousHost=rendezvousHost,
            rendezvousPort=rendezvousPort,
            topics=topics)

    def connect(self, rendezvousHost: str, rendezvousPort: int):
        self.rendezvous: RendezvousAuthenticatedConnection = RendezvousAuthenticatedConnection(
            signature=self.signature,
            key=self.key,
            host=rendezvousHost,  # '161.35.238.159',
            port=rendezvousPort,  # 49152,
            onMessage=self.handleRendezvousMessage)

    def sendTopics(self):
        ''' send our topics to the rendezvous server to get peer lists '''
        for topic in self.topics.keys():
            self.rendezvous.send(
                cmd=ToServerSubscribeProtocol.subscribePrefix,
                msgs=[
                    "signature doesn't matter during testing",
                    json.dumps({
                        **{'pubkey': 'wallet.pubkey'},
                        # **(
                        #    {
                        #        'publisher': [topic]}
                        # ),
                        **(
                            {
                                'subscriptions': [topic]
                            }
                        )})])
