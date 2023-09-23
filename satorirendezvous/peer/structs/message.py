import datetime as dt
from satorilib.api.time import now
from satorirendezvous.lib.lock import LockableList
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
    def isPing(self):
        return self.raw.startswith(PeerProtocol.pingPrefix)


class PeerMessages(LockableList[PeerMessage]):
    '''
    iterating over this list within a context manager is thread safe, example: 
        with messages:
            for message in messages:
                message.read()
    '''
