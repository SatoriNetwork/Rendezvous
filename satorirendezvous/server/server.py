import socket
import threading
import queue
from satorilib import logging
from behaviors import ConnectBehavior
# from behaviors.testing import PairBehavior
from behaviors.testing import ConnectAuthorizedBehavior
# from behaviors.testing import ConnectAuthorizedHeartBehavior
logging.setup(file='/tmp/rendezvous.log')


class RendezvousServer(ConnectAuthorizedBehavior):
    def __init__(self, port: int = 49152):
        super().__init__()
        self.portRange: set[int] = set(range(49153, 65536))  # 16,382 ports
        self.sock: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self.process)
        self.worker.start()

    def runForever(self):
        while True:
            # # for PairBehavior:
            # import time
            # time.sleep(10)
            # pass
            data, address = self.sock.recvfrom(1028)
            logging.debug('received: ', data, address)
            self.queue.put((data, address))
