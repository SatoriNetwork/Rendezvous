import socket
import datetime as dt
from satorirendezvous.lib.lock import LockableList
from satorirendezvous.peer.p2p.connect import Connection
from satorirendezvous.peer.structs.message import PeerMessage, PeerMessages


class Channel():
    ''' manages a single connection between two nodes over UDP '''

    def __init__(
        self,
        topic: str,
        ip: str,
        port: int,
        localPort: int,
        topicSocket: socket.socket,
    ):
        self.topic = topic
        self.messages: PeerMessages = (
            self.messages if hasattr(self, 'messages') else PeerMessages([]))
        self.connection = (
            self.connection if hasattr(self, 'connection') else Connection(
                topicSocket=topicSocket,
                peerIp=ip,
                peerPort=port,
                port=localPort,
                onMessage=self.add))
        self.connection.establish()

    def send(self, cmd: str, msgs: list[str] = None):
        self.connection.send(cmd, msgs)

    def add(
        self,
        message: bytes,
        sent: bool,
        time: dt.datetime = None,
        **kwargs
    ):
        with self.messages:
            self.messages.append(PeerMessage(
                sent=sent, raw=message, time=time))

    def orderedMessages(self):
        ''' most recent last messages by PeerMessage.time '''
        return sorted(self.messages, key=lambda msg: msg.time)

    def messagesAfter(self, time: dt.datetime):
        return [msg for msg in self.messages if msg.time > time]

    def receivedAfter(self, time: dt.datetime):
        return [
            msg for msg in self.messages
            if msg.time > time and not msg.sent]


class Channels(LockableList[Channel]):
    '''
    iterating over this list within a context manager is thread safe, example: 
        with channels:
            channels.append(channel)
    '''
