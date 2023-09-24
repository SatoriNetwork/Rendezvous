import time
import socket
import threading
from satorilib import logging
from satorirendezvous.client.structs.message import FromServerMessage
from satorirendezvous.client.structs.protocol import ToServerProtocol


class RendezvousConnection():
    ''' conn for server '''

    def __init__(
        self,
        host: str,
        port: int,
        timed: bool = True,
        onMessage: function = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.msgId = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.rendezvousServer = (host, port)
        self.onMessage = onMessage or self.display
        self.timed = timed
        self.listen = True
        self.inbox = []
        self.outbox = {}
        self.establish()

    def display(self, msg, addr):
        logging.info(f'from: {addr}, {msg}', print=True)

    def stop(self):
        self.listen = False
        self.listener.join()  # Wait for the thread to finish

    def establish(self):
        ''' connect to rendezvous '''
        logging.info('connecting to rendezvous server', print=True)
        self.listener = threading.Thread(target=self.hear, daemon=True)
        self.listener.start()
        # self.sock.sendto(b'0', self.rendezvousServer)
        self.checkin()

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
            data, _ = self.sock.recvfrom(1024)
            msg = FromServerMessage.fromBytes(data)
            try:
                self.inbox.append(msg)
            except Exception as e:
                logging.warning('error with inbox', e, data, print=True)
            self.onMessage(msg)

    def send(self, cmd: str, msgs: list[str] = None):
        ''' compiles a payload including msgId, updates outbox, and sends '''
        if not ToServerProtocol.isValidCommand(cmd):
            logging.error('command not valid', cmd, print=True)
            return
        try:
            payload = ToServerProtocol.compile([
                x for x in [cmd, str(self.msgId), *(msgs or [])]
                if isinstance(x, int) or (x is not None and len(x) > 0)])
            self.outbox[self.msgId] = payload
        except Exception as e:
            logging.warning('err w/ payload', e, cmd, self.msgId, msgs)
        self.sock.sendto(payload, self.rendezvousServer)
        self.msgId += 1

    def checkin(self):
        self.send(ToServerProtocol.checkinPrefix)
