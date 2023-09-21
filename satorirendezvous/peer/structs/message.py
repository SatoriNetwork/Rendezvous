import datetime as dt
from satorilib.api.time import now
from satorirendezvous.peer.structs.protocol import PeerProtocol


class PeerMessage():

    def __init__(self, sent: bool, raw: bytes, time: dt.datetime = None):
        self.raw = raw
        self.sent = sent
        self.time = time or now()

    @property
    def messageAsString(self):
        return self.raw.decode()

    @property
    def isConfirmedReady(self):
        return self.raw == PeerProtocol.confirmReady()

    @property
    def isResponse(self):
        return self.raw.startswith(PeerProtocol.respondPrefix())

    @property
    def isRequest(self):
        return self.raw.startswith(PeerProtocol.requestPrefix())

    @property
    def isReady(self):
        return self.raw.startswith(PeerProtocol.readyPrefix())

    @property
    def isBeat(self):
        return self.raw.startswith(PeerProtocol.beatPrefix())
