import json
from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorirendezvous.client.structs.protocol import ToServerProtocol


class ToServerMessage():
    ''' a strcuture describing a message from a client to the server '''

    @staticmethod
    def fromBytes(data: bytes, ip: str, port: int, sent: bool = False):
        parts = []
        command = None
        msgId = None
        message = None
        try:
            parts = data.split(b'|', 2)
            command = parts[0]
            msgId = parts[1]
        except Exception as e:
            logging.error('fromBytes error: ', e)
        if len(parts) > 2:
            message = parts[2]
        return ToServerMessage(sent, ip, port, command, msgId, message)

    def __init__(
        self,
        sent: bool,
        ip: str,
        port: int,
        command: bytes,
        msgId: bytes,
        message: bytes,
    ):
        self.malformed = False
        if command is None or msgId is None:
            self.malformed = True
        self.ip = ip
        self.port = port
        self.sent = sent
        self.commandBytes = command
        self.msgIdBytes = msgId
        self.messageBytes = message
        # broken out if present in message
        self.portsTaken = None
        self.setPortsTaken()

    def __str__(self) -> str:
        return ('ToServerMessage('
                f'malformed:{self.malformed},'
                f'ip:{self.ip},'
                f'port:{self.port},'
                f'sent:{self.sent},'
                f'commandBytes:{self.commandBytes},'
                f'msgIdBytes:{self.msgIdBytes},'
                f'messageBytes:{self.messageBytes},'
                f'portsTaken:{self.portsTaken},'
                f'signatureBytes:{self.signatureBytes},'
                f'keyBytes:{self.keyBytes})')

    @property
    def address(self) -> tuple[str, int]:
        return (self.ip, self.port)

    @property
    def command(self) -> str:
        return ToServerProtocol.toStr(self.commandBytes)

    @property
    def msgId(self) -> str:
        return ToServerProtocol.toStr(self.msgIdBytes)

    @property
    def message(self) -> str:
        return ToServerProtocol.toStr(self.messageBytes)

    def setPortsTaken(self):
        if self.isPortsTaken():
            try:
                self.portsTaken = TwoWayDictionary.fromDict(
                    json.loads(self.message))
            except Exception:
                self.portsTaken = TwoWayDictionary()
                self.malformed = True

    def isCheckIn(self, override: bytes = None):
        return (override or self.commandBytes) == ToServerProtocol.checkinPrefix

    def isPortsTaken(self, override: bytes = None):
        return (override or self.commandBytes) == ToServerProtocol.portsPrefix

    def isBeat(self, override: bytes = None):
        return (override or self.commandBytes) == ToServerProtocol.beatPrefix
