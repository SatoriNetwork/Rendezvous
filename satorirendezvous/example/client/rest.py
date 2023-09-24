from satorirendezvous.client.rest import RendezvousByRest
from satorirendezvous.client.structs.protocol import ToServerProtocol


class RendezvousByRestAuthenticated(RendezvousByRest):
    ''' conn for server, using signature and key for identity  '''

    def __init__(
        self,
        signature: str,
        key: str,
        host: str,
        port: int,
        timed: bool = True,
        onMessage: function = None,
        *args,
        **kwargs,
    ):
        self.signature = signature
        self.key = key
        super().__init__(
            host=host,
            port=port,
            timed=timed,
            onMessage=onMessage,
            *args, **kwargs)

    def checkin(self):
        ''' authenticated checkin '''
        # self.send(f'CHECKIN|{self.msgId}|{self.signature}|{self.key}')
        self.send(
            cmd=ToServerProtocol.checkinPrefix,
            msgs=[self.signature, self.key])
