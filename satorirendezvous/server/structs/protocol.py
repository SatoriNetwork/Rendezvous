from satorirendezvous.lib.protocol import Protocol


class ToClientProtocol(Protocol):
    '''
    a structure describing the various commands a client can send to the server
    '''

    responsePrefix: bytes = b'RESPONSE'
    connectPrefix: bytes = b'CONNECT'
    responseSignature: list[str] = ['msgId', 'msg']
    connectSignature: list[str] = ['topic', 'peerIp', 'peerPort', 'clientPort']

    @staticmethod
    def prefixes():
        return [
            ToClientProtocol.responsePrefix,
            ToClientProtocol.connectPrefix]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToClientProtocol.toBytes(cmd) in ToClientProtocol.prefixes()
