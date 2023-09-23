''' placeholder for something great '''
from satorirendezvous.lib.protocol import Protocol


class PeerProtocol(Protocol):

    pingPrefix: bytes = b'PING'

    @staticmethod
    def prefixes():
        return [PeerProtocol.pingPrefix]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return PeerProtocol.toBytes(cmd) in PeerProtocol.prefixes()
