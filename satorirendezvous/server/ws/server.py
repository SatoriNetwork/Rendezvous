import socket
import threading
import queue
from satorilib import logging
from satorirendezvous.server.behaviors import ClientConnect
logging.setup(file='/tmp/rendezvous.log')


class RendezvousServer:
    ''' the rendezvous server '''

    def __init__(self, port: int = 49152, behavior: ClientConnect = None):
        self.sock: socket.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.queue = queue.Queue()
        self.behavior = behavior or ClientConnect()
        self.behavior.setSock(self.sock)
        self.behavior.setQueue(self.queue)
        self.worker = threading.Thread(target=behavior.router)
        self.worker.start()

    def runForever(self):
        while True:
            data, address = self.sock.recvfrom(1028)
            self.queue.put((data, address))
