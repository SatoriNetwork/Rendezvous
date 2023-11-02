from satorirendezvous.client.structs.protocol import ToServerProtocol


class ToServerSubscribeProtocol(ToServerProtocol):
    ''' addition of Subscribe to the protocol '''

    subscribePrefix: bytes = b'SUBSCRIBE'

    @staticmethod
    def subscribe(signature: str, key: str) -> bytes:
        ''' SUBSCRIBE|msgId|signature|key '''
        if isinstance(signature, str):
            signature = signature.encode()
        if isinstance(key, str):
            key = key.encode()
        return (
            ToServerSubscribeProtocol.subscribePrefix +
            b'|' + signature +
            b'|' + key)

    @staticmethod
    def prefixes():
        return [
            ToServerSubscribeProtocol.checkinPrefix,
            ToServerSubscribeProtocol.portsPrefix,
            ToServerSubscribeProtocol.beatPrefix,
            ToServerSubscribeProtocol.subscribePrefix]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToServerSubscribeProtocol.toBytes(cmd) in ToServerSubscribeProtocol.prefixes()
