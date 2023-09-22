import socket
import datetime as dt
from time import sleep
from typing import Union
from satorilib.api.time import now
from satorirendezvous.peer.structs.message import PeerMessage
from satorirendezvous.peer.structs.protocol import PeerProtocol
from satorirendezvous.peer.channel import Channel


class Topic():
    ''' manages all our udp channels for a single topic '''

    # todo:
    # 3. why not have a callback for getOneObservation?
    # 4. shouldn't every msg have a unique id?
    # 5. if we had a unique id on messages we could match them to a request.

    def __init__(self, name: str, port: int):
        self.name = name
        self.channels: list[Channel] = []
        if port is not None:
            self.setPort(port)

    def setPort(self, port: int):
        self.port = port
        self.setSocket()

    def setSocket(self):
        # bind a port for this topic, each channel will get a peer port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))

    def create(self, ip: str, port: int, localPort: int):
        if self.port is None:
            self.setPort(localPort)
        self.channels.append(Channel(self.name, ip, port, localPort))

    def broadcast(self, msg: bytes):
        for channel in self.channels:
            channel.send(msg)

    def getOneObservation(self, time: dt.datetime):
        ''' time is of the most recent observation '''
        channels = self.channels
        msg = PeerProtocol.requestObservationBefore(time)
        sentTime = now()
        for channel in channels:
            channel.send(msg)
        sleep(5)  # wait for responses, natural throttle
        responses: list[Union[PeerMessage, None]] = [
            channel.mostRecentResponse(channel.responseAfter(sentTime))
            for channel in channels]
        responseMessages = [
            response.raw for response in responses
            if response is not None]
        mostPopularResponseMessage = max(
            responseMessages,
            key=lambda response: len([
                r for r in responseMessages if r == response]))
        # here we could enforce a threshold, like super majority or something,
        # by saying this message must make up at least 67% of the responses
        # but I don't think it's necessary for now.
        return mostPopularResponseMessage
