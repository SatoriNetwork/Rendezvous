'''
this holds the protocol for node-to-node communication over udp.

we first of all need a way know if we're connected and ready to talk. they'll
both send a message on repeat of "READY?" until the other responds with "READY!"
once they both get a response of ready and have responded ready they'll talk. 

"READY?"
"READY!"

the protocol consists of a request for an observation before a given time. and
a response with the observation. if there is no observation, NONE is returned:

"REQUEST|time"
"RESPONSE|time|data"
"RESPONSE|NONE|NONE"

'''
import datetime as dt
from satorilib.api.time import datetimeToString, datetimeFromString, now

from satorirendezvous.lib.protocol import Protocol


class PeerProtocol(Protocol):

    @staticmethod
    def readyPrefix() -> bytes:
        return b'READY'

    @staticmethod
    def requestPrefix() -> bytes:
        return b'REQUEST'

    @staticmethod
    def respondPrefix() -> bytes:
        return b'RESPOND'

    @staticmethod
    def askReady() -> str:
        return PeerProtocol.readyPrefix() + b'?'

    @staticmethod
    def confirmReady() -> str:
        return PeerProtocol.readyPrefix() + b'!'

    @staticmethod
    def requestObservationBefore(time: dt.datetime) -> bytes:
        if isinstance(time, dt.datetime):
            time = datetimeToString(time)
        if isinstance(time, str):
            time = time.encode()
        return PeerProtocol.requestPrefix() + b'|' + time

    @staticmethod
    def respondObservation(time: dt.datetime, data: str) -> bytes:
        if isinstance(data, str):
            data = data.encode()
        if isinstance(time, dt.datetime):
            time = datetimeToString(time)
        if isinstance(time, str):
            time = time.encode()
        return PeerProtocol.respondPrefix() + b'|' + time + b'|' + data

    @staticmethod
    def respondNoObservation() -> bytes:
        return PeerProtocol.respondPrefix() + b'|' + b'NONE|NONE'

    @staticmethod
    def prefixes():
        return [
            PeerProtocol.readyPrefix(),
            PeerProtocol.requestPrefix(),
            PeerProtocol.respondPrefix()]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return PeerProtocol.toBytes(cmd) in PeerProtocol.prefixes() or any([
            PeerProtocol.toBytes(cmd).startswith(prefix)
            for prefix in PeerProtocol.prefixes()
        ])
