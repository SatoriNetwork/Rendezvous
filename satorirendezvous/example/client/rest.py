from satorirendezvous.client.rest import RendezvousByRest
from satorirendezvous.client.structs.protocol import ToServerProtocol


class RendezvousByRestAuthenticated(RendezvousByRest):
    ''' conn for server, using signature and key for identity  '''

    def __init__(
        self,
        signature: str,
        signed: str,
        host: str,
        timed: bool = True,
        onMessage: function = None,
        *args,
        **kwargs,
    ):
        self.signature = signature
        self.signed = signed
        super().__init__(
            host=host,
            timed=timed,
            onMessage=onMessage,
            *args, **kwargs)

    def checkin(self):
        ''' authenticated checkin '''
        # self.send(f'CHECKIN|{self.msgId}|{self.signature}|{self.signed}')
        self.send(
            cmd=ToServerProtocol.checkinPrefix,
            msgs=[self.signature, self.signed])
