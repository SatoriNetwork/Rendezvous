import json
from satorirendezvous.example.client.structs.protocol import ToServerSubscribeProtocol
from satorirendezvous.server.structs.message import ToServerMessage


class ToServerSubscribeMessage(ToServerMessage):
    ''' a strcuture describing a message from a client to the server '''

    def __init__(
        self,
        sent: bool,
        ip: str,
        port: int,
        command: bytes,
        msgId: bytes,
        message: bytes,
    ):
        super.__init__(sent, ip, port, command, msgId, message)
        self.subscriptionsBytes = None
        self.publicationsBytes = None
        self.setSubscriptionsAndPublications()

    @property
    def subscriptions(self) -> list[str]:
        return json.loads(ToServerSubscribeProtocol.toStr(self.subscriptionsBytes))

    @property
    def publications(self) -> list[str]:
        return json.loads(ToServerSubscribeProtocol.toStr(self.publicationsBytes))

    def setSubscriptionsAndPublications(self):
        ''' sig|key|subscriptions|publications '''
        if self.isSubscribe() and self.messageBytes is not None:
            parts = self.messageBytes.split(b'|', 3)
            if len(parts) == 4:
                self.signatureBytes = parts[2]
                self.keyBytes = parts[3]
            else:
                self.malformed = True
            if (
                not isinstance(self.subscriptions, list) or
                not isinstance(self.publications, list)
            ):
                self.malformed = True

    # override

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return ToServerSubscribeProtocol.isValidCommand(
            cmd.encode() if isinstance(cmd, str) else cmd)

    def isSubscribe(self):
        return self.commandBytes == ToServerSubscribeProtocol.subscribePrefix
