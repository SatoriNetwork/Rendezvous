import time
import threading
from satorilib import logging
from satorirendezvous.client.structs.protocol import ToServerProtocol
from satorirendezvous.client.rest import RendezvousByRest
from satorirendezvous.peer.p2p.topic import Topic, Topics
from satorirendezvous.client.structs.message import FromServerMessage


class Peer():
    ''' manages connection to the rendezvous server '''

    def __init__(
        self,
        rendezvousHost: str,
        topics: list[str] = None,
        handlePeriodicCheckin: bool = True,
        periodicCheckinSeconds: int = 60*60*1,
    ):
        self.createTopics(topics or [ToServerProtocol.fullyConnectedKeyword])
        self.connect(rendezvousHost)
        if handlePeriodicCheckin:
            self.periodicCheckinSeconds = periodicCheckinSeconds
            self.periodicCheckin()

    def createTopics(self, topics: list[str]):
        self.topics: Topics = Topics({k: Topic(k) for k in topics})

    def periodicCheckin(self):
        self.checker = threading.Thread(target=self.checkin, daemon=True)
        self.checker.start()

    def checkin(self):
        while True:
            time.sleep(self.periodicCheckinSeconds)
            self.rendezvous.checkin()

    def connect(self, rendezvousHost: str):
        self.rendezvous: RendezvousByRest = RendezvousByRest(
            host=rendezvousHost,
            timed=True,
            onMessage=self.handleRendezvousMessage)

    def add(self, topic: str):
        with self.topics:
            self.topics[topic] = Topic(topic)

    def remove(self, topic: str):
        with self.topics:
            del (self.topics[topic])

    def handleRendezvousMessage(self, msg: FromServerMessage):
        ''' receives all messages from the rendezvous server '''
        if msg.isConnect:
            try:
                topic = msg.payload.get('topic')
                ip = msg.payload.get('peerIp')
                port = int(msg.payload.get('peerPort'))
                localPort = int(msg.payload.get('clientPort'))
                if topic is not None and ip is not None:
                    with self.topics:
                        if topic in self.topics.keys():
                            self.topics[topic].create(
                                ip=ip,
                                port=port,
                                localPort=localPort)
                        else:
                            logging.error('topic not found', topic, print=True)
            except ValueError as e:
                logging.error('error parsing message', e, print=True)
