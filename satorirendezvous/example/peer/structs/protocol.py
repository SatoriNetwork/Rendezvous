'''
the protocol consists of a request for an observation before a given time. and
a response with the observation. if there is no observation, NONE is returned:

"REQUEST|<observation or count>|time"
"RESPONSE|<observation or count>|time|data"
"RESPONSE|<observation or count>|NONE|NONE"

'''
import datetime as dt
from satorilib.api.time import datetimeToString, datetimeFromString, now

from satorirendezvous.lib.protocol import Protocol


class PeerProtocol(Protocol):

    pingPrefix: bytes = b'PING'
    requestPrefix: bytes = b'REQUEST'
    respondPrefix: bytes = b'RESPOND'
    observationSub: bytes = b'observation'
    countSub: bytes = b'count'

    @staticmethod
    def ping() -> bytes:
        return PeerProtocol.pingPrefix

    @staticmethod
    def request(time: dt.datetime, subcmd: bytes = None, msgId: int = -1) -> bytes:
        if isinstance(time, dt.datetime):
            time = datetimeToString(time)
        if isinstance(time, str):
            time = time.encode()
        if subcmd is None:
            subcmd = PeerProtocol.observationSub
        if isinstance(subcmd, str):
            subcmd = subcmd.encode()
        if isinstance(msgId, int):
            msgId = str(msgId)
        if isinstance(msgId, str):
            msgId = msgId.encode()
        return PeerProtocol.requestPrefix + b'|' + subcmd + b'|' + msgId + b'|' + time

    @staticmethod
    def respond(time: dt.datetime, data: str, subcmd: bytes = None, msgId: int = -1) -> bytes:
        if isinstance(data, float):
            data = str(data)
        if isinstance(data, int):
            data = str(data)
        if isinstance(data, str):
            data = data.encode()
        if isinstance(time, dt.datetime):
            time = datetimeToString(time)
        if isinstance(time, str):
            time = time.encode()
        if subcmd is None:
            subcmd = PeerProtocol.observationSub
        if isinstance(subcmd, str):
            subcmd = subcmd.encode()
        if isinstance(msgId, int):
            msgId = str(msgId)
        if isinstance(msgId, str):
            msgId = msgId.encode()
        return PeerProtocol.respondPrefix + b'|' + subcmd + b'|' + msgId + b'|' + time + b'|' + data

    @staticmethod
    def respondNone(subcmd: bytes = None) -> bytes:
        return PeerProtocol.respond(subcmd=subcmd, data=b'NONE', time=b'NONE')

    @staticmethod
    def prefixes():
        return [
            PeerProtocol.requestPrefix,
            PeerProtocol.respondPrefix]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return PeerProtocol.toBytes(cmd) in PeerProtocol.prefixes() or any([
            PeerProtocol.toBytes(cmd).startswith(prefix)
            for prefix in PeerProtocol.prefixes()
        ])
