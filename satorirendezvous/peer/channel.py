import socket
import datetime as dt
from satorilib.api.time import now
from satorirendezvous.lib.lock import LockableList
from satorirendezvous.peer.connect import Connection
from satorirendezvous.peer.structs.message import PeerMessage, PeerMessages


class Channel():
    ''' manages a single connection between two nodes over UDP '''

    def __init__(
        self,
        topic: str,
        ip: str,
        port: int,
        localPort: int,
        topicSocket: socket.socket
    ):
        self.topic = topic
        self.messages: PeerMessages = PeerMessages([])
        self.connection = Connection(
            topicSocket=topicSocket,
            peerIp=ip,
            peerPort=port,
            port=localPort,
            onMessage=self.add)
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
        with self.messages:
            return sorted(self.messages, key=lambda msg: msg.time)

    def messagesAfter(self, time: dt.datetime):
        with self.messages:
            return [msg for msg in self.messages if msg.time > time]


class Channels(LockableList[Channel]):
    '''
    iterating over this list within a context manager is thread safe, example: 
        with channels:
            for channel in channels:
                channel.send(msg)
    '''
