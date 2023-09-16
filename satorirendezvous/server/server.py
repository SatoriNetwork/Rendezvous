import socket
import threading
import queue
from satorilib import logging
from satorirendezvous.server.behaviors import ClientConnect
logging.setup(file='/tmp/rendezvous.log')


class RendezvousServer(ClientConnect):
    ''' the rendezvous server '''

    def __init__(self, port: int = 49152):
        super().__init__()
        self.sock: socket.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self.process)
        self.worker.start()

    def runForever(self):
        while True:
            data, address = self.sock.recvfrom(1028)
            logging.debug('received: ', data, address)
            self.queue.put((data, address))
