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


class ToServerProtocol():
    '''
    a structure describing the various commands a client can send to the server
    '''

    @staticmethod
    def toBytes(msg: str) -> bytes:
        return msg.encode()

    @staticmethod
    def fromBytes(msg: bytes) -> str:
        return msg.decode()

    @staticmethod
    def checkinPrefix() -> bytes:
        return b'CHECKIN'

    @staticmethod
    def portsPrefix() -> bytes:
        return b'PORTS'

    @staticmethod
    def beatPrefix() -> bytes:
        return b'BEAT'

    @staticmethod
    def portsTaken(ports: list[str]) -> bytes:
        if isinstance(ports, list):
            ports = ','.join(ports)
        if isinstance(ports, str):
            ports = ports.encode()
        return ToServerProtocol.portsPrefix() + b'|' + ports
