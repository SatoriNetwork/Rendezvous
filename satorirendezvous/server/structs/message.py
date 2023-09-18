import json
from satorilib import logging
from satorilib.concepts import TwoWayDictionary
from satorirendezvous.server.structs.protocol import ToServerProtocol


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

    @staticmethod
    def asStr(msg: bytes) -> str:
        if isinstance(msg, bytes):
            return msg.decode()
        if isinstance(msg, str):
            return msg
        # what else could it be?
        return str(msg)

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToServerProtocol.isValidCommand(
            cmd.encode() if isinstance(cmd, str) else cmd)

    def __init__(
        self,
        sent: bool,
        ip: str,
        port: int,
        command: bytes,
        msgId: bytes,
        message: bytes
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
        self.signatureBytes = None
        self.keyBytes = None
        self.setSignatureAndKey()
        self.command = ToServerMessage.asStr(self.commandBytes)
        self.msgId = ToServerMessage.asStr(self.msgIdBytes)
        self.message = ToServerMessage.asStr(self.messageBytes)
        self.signature = ToServerMessage.asStr(self.signatureBytes)
        self.key = ToServerMessage.asStr(self.keyBytes)

    @property
    def address(self):
        return (self.ip, self.port)

    def setSignatureAndKey(self):
        if self.isCheckIn() or self.isSubscribe():
            if self.messageBytes is not None:
                parts = self.messageBytes.split(b'|', 1)
                if len(parts) == 2:
                    self.signatureBytes = parts[0]
                    self.keyBytes = parts[1]
                else:
                    self.malformed = True

    def setPortsTaken(self):
        if self.isPortsTaken():
            try:
                self.portsTaken = TwoWayDictionary.fromDict(
                    json.loads(self.message))
            except Exception:
                self.portsTaken = TwoWayDictionary()
                self.malformed = True

    def isCheckIn(self):
        return self.commandBytes == ToServerProtocol.checkinPrefix()

    def isPortsTaken(self):
        return self.commandBytes == ToServerProtocol.portsPrefix()

    def isSubscribe(self):
        return self.commandBytes == ToServerProtocol.subscribePrefix()

    def isBeat(self):
        return self.commandBytes == ToServerProtocol.beatPrefix()
