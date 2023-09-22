''' this script describes a single connection between two nodes over UDP '''

import socket
import threading
from satorilib import logging


class Connection:
    ''' raw connection functionality '''

    def __init__(self, topicSocket: socket.socket, port: int, peerPort: int, peerIp: str, onMessage=None):
        self.port = port
        self.peerIp = peerIp
        self.peerPort = peerPort
        self.topicSocket = topicSocket
        self.onMessage = onMessage or self.display
        self.sock = None

    def display(self, msg, addr):
        logging.info(f'from: {addr}, {msg}')

    def show(self):
        logging.info(f'peer ip:  {self.peerIp}')
        logging.info(f'peer port: {self.peerPort}')
        logging.info(f'my port: {self.port}')

    def establish(self):
        def listen():
            while True:
                data, addr = self.sock.recvfrom(1024)
                self.onMessage(data, addr)

        logging.info('establishing connection')
        self.topicSocket.sendto(b'0', (self.peerIp, self.peerPort))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.peerPort))
        listener = threading.Thread(target=listen, daemon=True)
        listener.start()
        logging.info('ready to exchange messages\n')
        # add a heart beat process...

    def send(self, msg: bytes):
        ''' assumes msg is bytes'''
        if isinstance(msg, str):
            msg = msg.encode()
        self.sock.sendto(msg, (self.peerIp, self.port))
