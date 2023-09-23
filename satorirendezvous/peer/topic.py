import socket
from satorirendezvous.lib.lock import LockableDict
from satorirendezvous.peer.channel import Channel, Channels


class Topic():
    ''' manages all our udp channels for a single topic '''

    def __init__(self, name: str, port: int):
        self.name = name
        self.channels: Channels = Channels([])
        if port is not None:
            self.setPort(port)

    def setPort(self, port: int):
        self.port = port
        self.setSocket()

    def setSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))

    def create(self, ip: str, port: int, localPort: int):
        if self.port is None:
            self.setPort(localPort)
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
