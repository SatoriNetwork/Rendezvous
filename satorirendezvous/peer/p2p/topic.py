import time
import socket
import threading
from satorilib.api.time import now
from satorirendezvous.lib.lock import LockableDict
from satorirendezvous.peer.p2p.channel import Channel, Channels


class Topic():
    ''' manages all our udp channels for a single topic '''

    def __init__(self, name: str, port: int):
        self.name = name
        self.channels: Channels = (
            self.channels if hasattr(self, 'channels') else Channels([]))
        if port is not None:
            self.setPort(port)
        self.periodicPurge()

    def periodicPurge(self):
        self.purger = threading.Thread(target=self.purge, daemon=True)
        self.purger.start()

    def purge(self):
        while True:
            then = now()
            time.sleep(60*60*24)
            with self.channels:
                self.channels = [
                    channel for channel in self.channels
                    if len(channel.messagesAfter(time=then)) > 0]

    def setPort(self, port: int):
        self.port = port
        self.setSocket()

    def setSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))

    def findChannel(self, ip: str, port: int, localPort: int):
        for channel in self.channels:
            if (
                channel.connection.peerIp == ip and
                channel.connection.peerPort == port and
                channel.connection.port == localPort
            ):
                return channel
        return None

    def create(self, ip: str, port: int, localPort: int):
        if self.port is None:
            self.setPort(localPort)
        if self.findChannel(ip, port, localPort) is None:
            with self.channels:
                self.channels.append(Channel(
                    topic=self.name,
                    ip=ip,
                    port=port,
                    localPort=localPort,
                    topicSocket=self.sock))

    def broadcast(self, cmd: str, msgs: list[str] = None):
        for channel in self.channels:
            channel.send(cmd, msgs)


class Topics(LockableDict[str, Topic]):
    '''
    iterating over this dictionary within a context manager is thread safe, 
    example: 
        with topics:
            topics['topic'] = Topic('name', 1234)
    '''
