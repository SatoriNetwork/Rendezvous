from satorirendezvous.example.server.structs.protocol import ToServerSubscribeProtocol
from satorirendezvous.server.structs.message import ToServerMessage


class ToServerSubscribeMessage(ToServerMessage):
    ''' a strcuture describing a message from a client to the server '''

    # override
    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToServerSubscribeProtocol.isValidCommand(
            cmd.encode() if isinstance(cmd, str) else cmd)

    # override
    def setSignatureAndKey(self):
        if self.isCheckIn() or self.isSubscribe():
            if self.messageBytes is not None:
                parts = self.messageBytes.split(b'|', 1)
                if len(parts) == 2:
                    self.signatureBytes = parts[0]
                    self.keyBytes = parts[1]
                else:
                    self.malformed = True

    def isSubscribe(self):
        return self.commandBytes == ToServerSubscribeProtocol.subscribePrefix()
