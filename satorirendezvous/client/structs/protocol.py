"""
this holds the protocol for node-rendezvous communication over udp.

since only a very simple static protocol is needed, and we want to minimize 
package sizes this doesn't even use json. for any complicated communication
replacing the entire protocol is recommended.

client to server: 'COMMAND|msgId(|data)'
server to client: always responds with 'msgId(|response)'

all conversation is done over UDP, and in chunks of 1028 bytes or less.
the available commands are:
    CHECKIN - the client is checking in with the server
    CHECKIN|msgId|signature|idKey
    
    PORTS - the client is telling the server, not to assign it these ports
    PORTS|msgId|portsTaken
   
"""


from satorirendezvous.lib.protocol import Protocol


class ToServerProtocol(Protocol):
    '''
    a structure describing the various commands a client can send to the server
    '''

    checkinPrefix: bytes = b'CHECKIN'
    portsPrefix: bytes = b'PORTS'
    beatPrefix: bytes = b'BEAT'
    fullyConnectedKeyword = 'fullyConnected'

    @staticmethod
    def portsTaken(ports: list[str]) -> bytes:
        if isinstance(ports, list):
            ports = ','.join(ports)
        if isinstance(ports, str):
            ports = ports.encode()
        return ToServerProtocol.portsPrefix + b'|' + ports

    @staticmethod
    def checkin(msgId: str, signature: str, key: str) -> bytes:
        ''' CHECKIN|msgId|signature|key'''
        if isinstance(signature, str):
            signature = signature.encode()
        if isinstance(key, str):
            key = key.encode()
        if isinstance(msgId, int):
            msgId = str(msgId)
        if isinstance(msgId, str):
            msgId = msgId.encode()
        return ToServerProtocol.checkinPrefix + b'|' + msgId + b'|' + signature + b'|' + key

    @staticmethod
    def prefixes():
        return [
            ToServerProtocol.checkinPrefix,
            ToServerProtocol.portsPrefix,
            ToServerProtocol.beatPrefix]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToServerProtocol.toBytes(cmd) in ToServerProtocol.prefixes()
