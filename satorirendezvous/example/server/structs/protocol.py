from satorirendezvous.server.structs.protocol import ToServerProtocol


class ToServerSubscribeProtocol(ToServerProtocol):
    ''' addition of Subscribe to the protocol '''

    @staticmethod
    def subscribePrefix() -> bytes:
        ''' SUBSCRIBE - the client is subscribing to one or more topics '''
        return b'SUBSCRIBE'

    @staticmethod
    def subscribe(signature: str, key: str) -> bytes:
        ''' SUBSCRIBE|msgId|signature|key '''
        if isinstance(signature, str):
            signature = signature.encode()
        if isinstance(key, str):
            key = key.encode()
        return ToServerProtocol.subscribePrefix() + b'|' + signature + b'|' + key

    @staticmethod
    def prefixes():
        return [
            ToServerSubscribeProtocol.checkinPrefix(),
            ToServerSubscribeProtocol.portsPrefix(),
            ToServerSubscribeProtocol.beatPrefix(),
            ToServerSubscribeProtocol.subscribePrefix()]
