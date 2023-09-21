from satorirendezvous.lib.protocol import Protocol


class ToClientProtocol(Protocol):
    '''
    a structure describing the various commands a client can send to the server
    '''

    @staticmethod
    def responsePrefix() -> bytes:
        return b'RESPONSE'

    @staticmethod
    def connectPrefix() -> bytes:
        return b'CONNECT'

    @staticmethod
    def prefixes():
        return [
            ToClientProtocol.responsePrefix(),
            ToClientProtocol.connectPrefix(),
        ]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToClientProtocol.toBytes(cmd) in ToClientProtocol.prefixes() 
            