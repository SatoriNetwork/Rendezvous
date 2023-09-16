import random
from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorilib.api.udp.rendezvous import UDPRendezvousMessage


class RendezvousClient:
    ''' a structure to hold the data for a client connection '''

    def __init__(
        self,
        address: tuple[str, int],
        ip: str,
        port: int = 49152,  # rendezvous connection port
        portsTaken: TwoWayDictionary[int, str] = None,
    ):
        # self reported - these are basically a blacklist
        self.portsTaken: TwoWayDictionary[str,
                                          int] = portsTaken or TwoWayDictionary()
        # server assigned - added to the blacklist of unavailable ports
        self.portsAssigned: TwoWayDictionary[str, int] = TwoWayDictionary()
        self.ip: str = ip
        self.port: int = port
        self.address: tuple[str, int] = address
        self.msgs: list[UDPRendezvousMessage] = []

    def addMsg(self, msg: UDPRendezvousMessage):
        self.msgs.append(msg)

    @property
    def msg(self):
        if len(self.msgs) == 0:
            return None
        return self.msgs[-1]

    def portFor(self, streamId: str):
        return self.portsAssigned.get(streamId)

    def blacklistedPorts(self):
        return set(list(self.portsTaken.values()) + list(self.portsAssigned.values()))

    def availablePorts(self, portRange: list[int]):
        return [p for p in portRange if p not in self.blacklistedPorts()]

    def randomAvailablePort(self, portRange: list[int]):
        if isinstance(portRange, set):
            portRange = list(portRange)
        logging.debug('portRange:', len(portRange))
        blacklist = self.blacklistedPorts()
        logging.debug('blacklist:', blacklist)
        if len(blacklist) > 0:
            port = next(iter(blacklist))
        else:
            return random.choice(portRange)
        logging.debug('port11:', port)
        x = 0
        while port in blacklist:
            port = random.choice(portRange)
            x += 1
            if x > len(portRange):
                # catch this, don't crash the server.
                raise Exception(
                    'unable to find an available port in the range: {}'.format(portRange))
        logging.debug('port2:', port)
        return port
