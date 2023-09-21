'''
our (persistent) connection to the rendezvous server, turns out we don't 
actually need a persistent connection. so we'ved move away from this design.
'''

import time
import threading
import socket
from satorilib import logging
from satorirendezvous.client.behaviors.base import EstablishConnection
from satorirendezvous.server.structs.message import ToServerMessage
from satorirendezvous.client.structs.protocol import ToServerProtocol


class MaintainConnection(EstablishConnection):
    ''' 
    uses a heart beat 3 times every 5 minutes to persist a connection with the
    server.
    '''

    def __init__(
        self,
        serverHost: str,
        serverPort: int,
        onMessage: function = None,
        socket: socket.socket = None
    ):
        super().__init__(serverHost, serverPort, onMessage, socket)
        self.lastBeat = 0.0
        self.maintain()

    def display(self, msg, addr):
        logging.info(f'from: {addr}, {msg}', print=True)

    def show(self):
        logging.info(f'my port: {self.port}', print=True)

    def maintain(self):
        def heartbeat():
            '''
            sends heartbeat to rendezvous server 3 times per 5 minutes,
            unless received a heartbeat from server, then skip 1.
            '''
            beats = 0
            skip = True
            while True:
                logging.info(
                    f'heartbeat {beats}, {skip}, {self.lastBeat}', print=True)
                if not skip:
                    beats -= 1
                    self.send(ToServerProtocol.beatPrefix(), beats)
                skip = False
                time.sleep(99)
                if self.lastBeat > time.time() - 99:
                    skip = True
        logging.info('ready to exchange messages\n', print=True)
        self.heart = threading.Thread(target=heartbeat, daemon=True)
        self.heart.start()
