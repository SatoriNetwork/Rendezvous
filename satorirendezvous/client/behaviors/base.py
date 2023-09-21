''' connects to the rendezvous server '''
import time
import threading
import socket
from satorilib import logging
from satorirendezvous.client.structs.message import FromServerMessage
from satorirendezvous.client.structs.protocol import ToServerProtocol


class EstablishConnection:
    ''' raw connection functionality '''

    def __init__(
        self,
        serverHost: str,
        serverPort: int,
        onMessage: function = None,
        socket: socket.socket = None,
        timed: bool = True,
    ):
        # could allow us to keep track of which messages were responded to
        self.msgId = 0
        self.sock: socket.socket = socket
        self.rendezvousServer = (serverHost, serverPort)
        self.onMessage = onMessage or self.display
        self.port = None
        self.inbox = []
        self.outbox = {}
        self.listen = True
        self.timed = timed

    def display(self, msg, addr):
        logging.info(f'from: {addr}, {msg}', print=True)

    def show(self):
        logging.info(f'my port: {self.port}', print=True)

    def stop(self):
        self.listen = False
        self.listener.join()  # Wait for the thread to finish

    def establish(self):
        ''' connect to rendezvous '''
        logging.info('connecting to rendezvous server', print=True)
        self.listener = threading.Thread(target=self.hear, daemon=True)
        self.listener.start()
        # self.sock.sendto(b'0', self.rendezvousServer)
        self.send(ToServerProtocol.checkinPrefix())

    def hear(self):
        '''
        listen for messages from rendezvous server
        saves message to inbox
        message from server is of this format: f'{command}|{msgId}|{msgs}...'
        or f'{command}|{msgs}...'
        calls the callback function with the message and address            
        '''
        if self.timed:
            start = time.time()
        while self.listen and (
                (not self.timed) or
                (time.time() - start > 5*60)
        ):
            data, addr = self.sock.recvfrom(1024)
            msg = FromServerMessage.fromBytes(data)
            try:
                self.inbox.append(msg)
            except Exception as e:
                logging.warning('error with inbox', e, data, print=True)
            self.onMessage(data, addr)

    def send(self, cmd: str, msgs: list[str] = None):
        ''' compiles a payload including msgId, updates outbox, and sends '''
        if not ToServerProtocol.isValidCommand(cmd):
            logging.error('command not valid', cmd, print=True)
            return
        try:
            payload = ToServerProtocol.compile([
                x for x in [cmd, str(self.msgId), *msgs]
                if isinstance(x, int) or (x is not None and len(x) > 0)])
            self.outbox[self.msgId] = payload
        except Exception as e:
            logging.warning('err w/ payload', e, cmd, self.msgId, msgs)
        self.sock.sendto(payload, self.rendezvousServer)
        self.msgId += 1
