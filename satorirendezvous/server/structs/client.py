from typing import Union
import random
import time
from satorilib.concepts import TwoWayDictionary
from satorirendezvous.lib.lock import LockableList
from satorirendezvous.server.structs.message import ToServerMessage


class RendezvousClient:
    ''' a structure describing a client's connection '''

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
        self.msgs: list[ToServerMessage] = []
        self.seen()

    def __str__(self) -> str:
        return f'RendezvousClient({self.address}, {len(self.msgs)})'

    def addMsg(self, msg: ToServerMessage):
        self.seen()
        self.msgs.append(msg)

    def seen(self):
        self.lastSeen = time.time()

    @property
    def msg(self):
        if len(self.msgs) == 0:
            return None
        return self.msgs[-1]

    def portFor(self, streamId: str) -> Union[int, None]:
        return self.portsAssigned.get(streamId)

    def blacklistedPorts(self):
        return set(list(self.portsTaken.values()) + list(self.portsAssigned.values()))

    def availablePorts(self, portRange: list[int]):
        return [p for p in portRange if p not in self.blacklistedPorts()]

    def randomAvailablePort(self, portRange: list[int]):
        if isinstance(portRange, set):
            portRange = list(portRange)
        blacklist = self.blacklistedPorts()
        if len(blacklist) > 0:
            port = next(iter(blacklist))
        else:
            return random.choice(portRange)
        x = 0
        while port in blacklist:
            port = random.choice(portRange)
            x += 1
            if x > len(portRange):
                # catch this, don't crash the server.
                raise Exception(
                    'unable to find an available port in the range: '
                    f'{portRange}')
        return port


class RendezvousClients(LockableList[RendezvousClient]):
    ''' iterating over this list within a context manager is thread safe '''
