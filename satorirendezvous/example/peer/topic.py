from time import sleep
from typing import Union
import datetime as dt
import socket
from satorilib.api.time import now
from satorilib.concepts import StreamId
from satorirendezvous.peer.structs.message import PeerMessage
from satorirendezvous.peer.structs.protocol import PeerProtocol
from satorirendezvous.peer.channel import Channel

class Topic():
    ''' manages all our udp channels for a single topic '''

    # todo:
    # 0. we should be using topics not streamIds
    # 1. why must we filter down to ready channels?
    # 2. why ever have ready channels?
    # 3. why not have a callback for getOneObservation?
    # 4. shouldn't every msg have a unique id?
    # 5. if we had a unique id on messages we could match them to a request.

    def __init__(self, streamId: StreamId, port: int):
        self.streamId = streamId
        self.channels: list[Channel] = []
        # bind a port for this topic, each channel will get a peer port
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.port))

    def readyChannels(self) -> list[Channel]:
        return [channel for channel in self.channels if channel.isReady()]

    def create(self, ip: str, port: int, localPort: int):
        print(f'CREATING: {ip}:{port},{localPort}')
        self.channels.append(Channel(self.streamId, ip, port, localPort))

    def broadcast(self, msg: bytes):
        for channel in self.readyChannels():
            channel.send(msg)

    def getOneObservation(self, time: dt.datetime):
        ''' time is of the most recent observation '''
        channels = self.readyChannels()
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
