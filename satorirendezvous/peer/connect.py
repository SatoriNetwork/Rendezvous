''' this script describes a single connection between two nodes over UDP '''

import socket
import threading
from typing import Union
from satorilib import logging
from satorilib.api.time import now
from satorirendezvous.peer.structs.protocol import PeerProtocol


class Connection:
    ''' raw connection functionality '''

    def __init__(self, topicSocket: socket.socket, port: int, peerPort: int, peerIp: str, onMessage=None):
        self.port = port
        self.peerIp = peerIp
        self.peerPort = peerPort
        self.topicSocket = topicSocket
        self.onMessage = onMessage or self.display
        self.sock = None

    def display(self, msg, addr=None, **kwargs):
        logging.info(f'from: {addr}, {msg}')

    def show(self):
        logging.info(f'peer ip:  {self.peerIp}')
        logging.info(f'peer port: {self.peerPort}')
        logging.info(f'my port: {self.port}')

    def establish(self):

        def punchAHole():
            self.topicSocket.sendto(b'0', (self.peerIp, self.peerPort))

        def listen():
            while True:
                data, addr = self.sock.recvfrom(1024)
                self.onMessage(data, sent=False, time=now(), addr=addr)

        logging.info('establishing connection')
        punchAHole()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.peerPort))
        listener = threading.Thread(target=listen, daemon=True)
        listener.start()
        logging.info('ready to exchange messages\n')
        # todo:  add a heart beat ping if needed

    def makePayload(self, cmd: str, msgs: list[str] = None) -> Union[bytes, None]:
        if not PeerProtocol.isValidCommand(cmd):
            logging.error('command not valid', cmd, print=True)
            return None
        try:
            return PeerProtocol.compile([
                x for x in [cmd, *(msgs or [])]
                if isinstance(x, int) or (x is not None and len(x) > 0)])
        except Exception as e:
            logging.warning('err w/ payload', e, cmd, msgs)

    def send(self, cmd: str, msgs: list[str] = None):
        payload = self.makePayload(cmd, msgs)
        if payload is None:
            return False
        self.sock.sendto(payload, (self.peerIp, self.port))
        self.onMessage(msgs, sent=True, time=now())
        return True
