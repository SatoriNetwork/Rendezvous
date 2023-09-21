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
                if command == ToClientProtocol.responsePrefix():
                    msgId = int(parts[1])
                    message = data.split('|')[2:]
                elif command == ToClientProtocol.connectPrefix():
                    msgId = None
                    message = data.split('|')[1:]
            return FromServerMessage(command, msgId, message)
        except Exception as e:
            logging.error('fromBytes error: ', e, print=True)
            return FromServerMessage(raw=data)

    def __init__(
        self,
        command: Union[str, None] = None,
        msgId: Union[int, None] = None,
        messages: Union[list[str], None] = None,
        raw: bytes = None,
    ):
        self.command = command
        self.msgId = msgId
        self.messages = messages
        self.raw = raw

    @property
    def commandBytes(self):
        return ToClientProtocol.toBytes(self.command)

    @property
    def isResponse(self):
        return self.commandBytes == ToClientProtocol.responsePrefix()

    @property
    def isConnect(self):
        return self.commandBytes == ToClientProtocol.connectPrefix()
