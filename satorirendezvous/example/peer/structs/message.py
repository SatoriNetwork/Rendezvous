from typing import Union
import datetime as dt
from satorilib.api.time import now
from satorirendezvous.lib.lock import LockableList
from satorirendezvous.peer.structs.message import PeerMessage as BasePeerMessage
from satorirendezvous.example.peer.structs.protocol import PeerProtocol


class PeerMessage(BasePeerMessage):

    def __init__(
        self, sent: bool, raw: bytes, time: dt.datetime = None,
        prefix: Union[str, None] = None,
        subCommand: Union[str, None] = None,
        observationTime: Union[str, None] = None,
        data: Union[str, None] = None,
    ):
        self.raw: bytes = raw
        self.sent: bool = sent
        self.time: dt.datetime = time or now()
        self.prefix: Union[str, None] = prefix
        self.subCommand: Union[str, None] = subCommand
        self.observationTime: Union[str, None] = observationTime
        self.data: Union[str, None] = data
        self.initiateInterpret()

    def initiateInterpret(self):
        if (
            self.prefix is None and
            self.subCommand is None and
            self.observationTime is None and
            self.data is None
        ):
            self.interpret()

    def __eq__(self, __value: object) -> bool:
        return self.raw == __value.raw

    def interpret(self):
        try:
            parts = self.messageAsString.split('|')
            if self.isRequest:
                self.prefix = parts[0]
                self.subCommand = parts[1]
                self.observationTime = parts[2]
            elif self.isResponse:
                self.prefix = parts[0]
                self.subCommand = parts[1]
                self.observationTime = parts[2]
                self.data = parts[3]
        except Exception as e:
            print(e)

    @staticmethod
    def parse(raw: Union[str, bytes], sent: bool, time: dt.datetime = None) -> 'PeerMessage':
        if isinstance(raw, str):
            strRaw = raw
        elif isinstance(raw, bytes):
            strRaw = PeerMessage._asString(raw)
        else:
            strRaw = str(raw)
        try:
            parts = strRaw.split('|')
            if PeerMessage._isRequest(raw):
                PeerMessage(
                    raw=raw, sent=sent, time=time,
                    prefix=parts[0],
                    subCommand=parts[1],
                    observationTime=parts[2])
            elif PeerMessage._isResponse(raw):
                PeerMessage(
                    raw=raw, sent=sent, time=time,
                    prefix=parts[0],
                    subCommand=parts[1],
                    observationTime=parts[2],
                    data=parts[3])
        except Exception as e:
            print(e)

    @staticmethod
    def _asString(raw: bytes) -> str:
        return raw.decode()

    @staticmethod
    def _isResponse(raw: bytes, subcmd: bytes = None) -> bool:
        return raw.startswith(PeerProtocol.respondPrefix + b'|' + (subcmd if subcmd is not None else b''))

    @staticmethod
    def _isRequest(raw: bytes, subcmd: bytes = None) -> bool:
        return raw.startswith(PeerProtocol.requestPrefix + b'|' + (subcmd if subcmd is not None else b''))

    @staticmethod
    def _isNoneResponse(raw: bytes, subcmd: bytes = None) -> bool:
        return raw.endswith(b'NONE|NONE') and PeerMessage._isResponse(subcmd=subcmd)

    @property
    def messageAsString(self) -> str:
        return self.raw.decode()

    def isResponse(self, subcmd: bytes = None) -> bool:
        return PeerMessage._isResponse(self.raw, subcmd=subcmd)

    def isRequest(self, subcmd: bytes = None) -> bool:
        return PeerMessage.isRequest(self.raw, subcmd=subcmd)

    def isNoneResponse(self, subcmd: bytes = None) -> bool:
        return PeerMessage._isNoneResponse(self.raw, subcmd=subcmd)


class PeerMessages(LockableList[PeerMessage]):
    '''
    iterating over this list within a context manager is thread safe, example: 
        with messages:
            for message in messages:
                message.read()
    '''
