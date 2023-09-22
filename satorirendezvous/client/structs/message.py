from typing import Union
from satorilib import logging
from satorirendezvous.server.structs.protocol import ToClientProtocol


class FromServerMessage():
    ''' a strcuture describing a message from the server '''

    @staticmethod
    def fromBytes(data: bytes):
        try:
            parts = data.split(b'|')
            command = parts[0]
            if not ToClientProtocol.isValidCommand(data.split('|')[0]):
                logging.warning('invalid command', data, print=True)
            else:
                payload = None
                msgId = None
                if command == ToClientProtocol.responsePrefix:
                    msgId = int(parts[1])
                    messages = data.split('|')[2:]
                    if len(messages) == ToClientProtocol.responseSignature():
                        payload = {
                            k: v for k, v in zip(
                                ToClientProtocol.responseSignature(),
                                messages)}
                        messages = None
                elif command == ToClientProtocol.connectPrefix:
                    messages = data.split('|')[1:]
                    if len(messages) == ToClientProtocol.connectSignature():
                        payload = {
                            k: v for k, v in zip(
                                ToClientProtocol.connectSignature(),
                                messages)}
                        messages = None
            return FromServerMessage(command, msgId, messages, payload)
        except Exception as e:
            logging.error('fromBytes error: ', e, print=True)
            return FromServerMessage(raw=data)

    def __init__(
        self,
        command: Union[str, None] = None,
        msgId: Union[int, None] = None,
        messages: Union[list[str], None] = None,
        payload: Union[dict[str, str], None] = None,
        raw: Union[bytes, None] = None,
    ):
        self.command = command
        self.msgId = msgId
        self.messages = messages
        self.payload: dict = payload or {}
        self.raw: Union[bytes, None] = raw

    @property
    def commandBytes(self):
        return ToClientProtocol.toBytes(self.command)

    @property
    def isResponse(self):
        return self.commandBytes == ToClientProtocol.responsePrefix

    @property
    def isConnect(self):
        return self.commandBytes == ToClientProtocol.connectPrefix
