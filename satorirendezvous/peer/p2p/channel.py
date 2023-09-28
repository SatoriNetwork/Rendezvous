import time
import socket
import threading
import datetime as dt
from satorirendezvous.lib.lock import LockableList
from satorirendezvous.peer.p2p.connect import Connection
from satorirendezvous.peer.structs.message import PeerMessage, PeerMessages
from satorirendezvous.peer.structs.protocol import PeerProtocol


class Channel():
    ''' manages a single connection between two nodes over UDP '''

    def __init__(
        self,
        topic: str,
        ip: str,
        port: int,
        localPort: int,
        topicSocket: socket.socket,
        ping: bool = True,
    ):
        self.topic = topic
        self.messages: PeerMessages = (
            self.messages if hasattr(self, 'messages') else PeerMessages([], limit=100))
        self.connection = (
            self.connection if hasattr(self, 'connection') else Connection(
                topicSocket=topicSocket,
                peerIp=ip,
                peerPort=port,
                port=localPort,
                onMessage=self.onMessage))
        self.connection.establish()
        if ping:
            self.setupPing()

    def setupPing(self):

        def pingForever(interval=60*28):
            while True:
                time.sleep(interval)
                self.send(cmd=PeerProtocol.pingPrefix)

        self.pingThread = threading.Thread(target=pingForever)
        self.pingThread.start()

    def send(self, cmd: str, msgs: list[str] = None):
        self.connection.send(cmd, msgs)

    def isReady(self) -> bool:
        return len(self.receivedAfter(time=dt.datetime.now() - dt.timedelta(minutes=28))) > 0
    
    # override
    def onMessage(
        self,
        message: bytes,
        sent: bool,
        time: dt.datetime = None,
        **kwargs,
    ):
        self.add(message=PeerMessage(sent=sent, raw=message, time=time))
        
    # override
    def add(self, message: PeerMessage):
        with self.messages:
            self.messages.append(message)

    def orderedMessages(self) -> list[PeerMessage]:
        ''' most recent last messages by PeerMessage.time '''
        return sorted(self.messages, key=lambda msg: msg.time)

    def messagesAfter(self, time: dt.datetime) -> list[PeerMessage]:
        return [msg for msg in self.messages if msg.time > time]

    def receivedAfter(self, time: dt.datetime) -> list[PeerMessage]:
        return [
            msg for msg in self.messages
            if msg.time > time and not msg.sent]


class Channels(LockableList[Channel]):
    '''
    iterating over this list within a context manager is thread safe, example: 
        with channels:
            channels.append(channel)
    '''
