
from satorirendezvous.lib.lock import LockableDict
from satorirendezvous.server.structs.client import RendezvousClient


class RendezvousClientsBySubscription(LockableDict[str, list[RendezvousClient]]):
    ''' iterating over this list within a context manager is thread safe '''
