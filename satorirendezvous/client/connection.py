''' our (persistent) connection to the rendezvous server '''
import socket
from satorirendezvous.client.behaviors.base import EstablishConnection
from satorirendezvous.client.structs.protocol import ToServerProtocol


class RendezvousConnection():
    ''' conn for server, using signature and key for identity  '''

    def __init__(
        self,
        signature: str,
        key: str,
        host: str,
        port: int,
        onMessage: function = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.signature = signature
        self.key = key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.behavior = EstablishConnection(
            host,
            port,
            onMessage,
            socket=self.sock)

    def checkin(self):
        # self.send(f'CHECKIN|{self.msgId}|{self.signature}|{self.key}')
        self.behavior.send(
            cmd=ToServerProtocol.checkinPrefix(),
            msg=[self.signature, self.key])
