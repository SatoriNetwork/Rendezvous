from typing import Union
import datetime as dt
from satorilib.api.time import now
from satorirendezvous.lib.lock import LockableList
from satorirendezvous.peer.structs.message import PeerMessage as BasePeerMessage
from satorirendezvous.example.peer.structs.protocol import PeerProtocol


class PeerMessage(BasePeerMessage):

    def __init__(self, sent: bool, raw: bytes, time: dt.datetime = None):
        self.raw = raw
        self.sent = sent
        self.time = time or now()
        self.prefix: Union[str, None] = None
        self.observationTime: Union[str, None] = None
        self.data: Union[str, None] = None
        self.interpret()

    def __eq__(self, __value: object) -> bool:
        return self.raw == __value.raw

    def interpret(self):
        try:
            parts = self.messageAsString().split('|')
            if self.isRequest:
                self.prefix = parts[0]
                self.observationTime = parts[1]
            elif self.isResponse:
                self.prefix = parts[0]
                self.observationTime = parts[1]
                self.data = parts[2]
        except Exception as e:
            print(e)

    @property
    def messageAsString(self):
        return self.raw.decode()

    @property
    def isResponse(self, subcmd: bytes = None):
        return self.raw.startswith(PeerProtocol.respondPrefix + ((b'|' + subcmd) if subcmd is not None else b'|'))

    @property
    def isRequest(self, subcmd: bytes = None):
        return self.raw.startswith(PeerProtocol.requestPrefix + ((b'|' + subcmd) if subcmd is not None else b'|'))

    @property
    def isNoneResponse(self, subcmd: bytes = None):
        return self.raw.endswith(b'NONE|NONE') and self.isResponse(subcmd=subcmd)


class PeerMessages(LockableList[PeerMessage]):
    '''
    iterating over this list within a context manager is thread safe, example: 
        with messages:
            for message in messages:
                message.read()
    '''
