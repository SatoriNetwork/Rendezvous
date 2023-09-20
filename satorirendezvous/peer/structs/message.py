import datetime as dt
from satorilib.api.time import now
from satorirendezvous.peer.structs.protocol import PeerProtocol


class PeerMessage():
    def __init__(self, sent: bool, message: bytes, time: dt.datetime = None):
        self.message = message
        self.sent = sent
        self.time = time or now()

    def messageAsString(self):
        return self.message.decode()

    def isConfirmedReady(self):
        return self.message == PeerProtocol.confirmReady()

    def isResponse(self):
        return self.message.startswith(PeerProtocol.respondPrefix())

    def isRequest(self):
        return self.message.startswith(PeerProtocol.requestPrefix())

    def isReady(self):
        return self.message.startswith(PeerProtocol.readyPrefix())

    def isBeat(self):
        return self.message.startswith(PeerProtocol.beatPrefix())
