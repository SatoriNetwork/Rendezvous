import time
import threading
from satorilib import logging
from satorirendezvous.client.structs.protocol import ToServerProtocol
from satorirendezvous.client.connection import RendezvousConnection
from satorirendezvous.peer.topic import Topic, Topics
from satorirendezvous.client.structs.message import FromServerMessage


class Peer():
    ''' manages connection to the rendezvous server '''

    def __init__(
        self,
        rendezvousHost: str,
        rendezvousPort: int,
        topics: list[str] = None,
        handlePeriodicCheckin: bool = True,
        periodicCheckinSeconds: int = 60*60*1
    ):
        topics = topics or [ToServerProtocol.fullyConnectedKeyword]
        self.topics: Topics = Topics({k: Topic(k) for k in topics})
        self.connect(rendezvousHost, rendezvousPort)
        if handlePeriodicCheckin:
            self.periodicCheckinSeconds = periodicCheckinSeconds
            self.periodicCheckin()

    def periodicCheckin(self):
        self.checker = threading.Thread(target=self.checker, daemon=True)
        self.checker.start()

    def checkin(self):
        while True:
            time.sleep(self.periodicCheckinSeconds)
            self.rendezvous.establish()

    def connect(self, rendezvousHost: str, rendezvousPort: int):
        self.rendezvous: RendezvousConnection = RendezvousConnection(
            host=rendezvousHost,
            port=rendezvousPort,
            timed=True,
            onMessage=self.handleRendezvousMessage)

    def add(self, topic: str):
        self.topics[topic] = Topic(topic)

    def handleRendezvousMessage(self, msg: FromServerMessage):
        ''' receives all messages from the rendezvous server '''
        if msg.isConnect():
            try:
                topic = msg.payload.get('topic')
                ip = msg.payload.get('peerIp')
                port = int(msg.payload.get('peerPort'))
                localPort = int(msg.payload.get('clientPort'))
                if topic is not None and ip is not None:
                    if topic in self.topics.keys():
                        self.topics[topic].create(
                            ip=ip,
                            port=port,
                            localPort=localPort)
                    else:
                        logging.error('topic not found', topic, print=True)
            except ValueError as e:
                logging.error('error parsing message', e, print=True)
