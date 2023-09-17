import time
from satorilib import logging
logging.setup(file='/tmp/rendezvous.log')


class Pair():
    '''
    a simple response behavior - pair clients together two by two, first come, 
    first serve, without any authorization.
    '''

    def __init__(self, *args, **kwargs):
        logging.info('starting rendezvous server...')
        self.clients = []

    def process(self):
        logging.info('starting rendezvous worker...')
        while True:
            self.clients = []
            while True:
                data, address = self.sock.recvfrom(128)
                logging.info(data, 'from', address)
                self.clients.append(address)
                self.sock.sendto(b'ready', address)
                if len(self.clients) == 2:
                    logging.info('got 2 clients, sending details to each')
                    break
            c1 = self.clients.pop()
            c1_addr, c1_port = c1
            c2 = self.clients.pop()
            c2_addr, c2_port = c2
            self.sock.sendto(f'{c1_addr} {c1_port} {c2_port}'.encode(), c2)
            self.sock.sendto(f'{c2_addr} {c2_port} {c1_port}'.encode(), c1)

    # there should be to need to override this
    def runForever(self):
        while True:
            time.sleep(10)
