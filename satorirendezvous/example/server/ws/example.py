from satorirendezvous.server import RendezvousServer

from satorirendezvous.example.server.behaviors.subscribe import SubscribingClientConnect


def exampleUse():
    ''' 
    example of how to extend and thereby use the satorirendezvous package
    '''
    RendezvousServer(
        behavior=SubscribingClientConnect(),
        port=49152,
    ).runForever()


# or use the flask app
