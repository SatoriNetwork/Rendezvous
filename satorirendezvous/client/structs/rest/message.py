import json
from typing import Union
from satorilib import logging
from satorirendezvous.server.structs.rest import ToClientRestProtocol as Protocol


class FromServerMessage():
    ''' a strcuture describing a message from the server '''

    def __init__(
        self,
        command: Union[str, None] = None,
        msgId: Union[int, None] = None,
        messages: Union[list[str], None] = None,
        raw: Union[str, None] = None,
    ):
        self.command = command
        self.msgId = msgId
        self.messages = messages
        self.raw = raw

    @staticmethod
    def fromJson(data: str):
        logging.debug('fromStr---: ', data, print='teal')
        try:
            return FromServerMessage(**json.loads(data))
        except Exception as e:
            logging.error('FromServerMessage.fromJson error: ',
                          e, data, print=True)
            return FromServerMessage(raw=data)

    @property
    def isResponse(self) -> bool:
        return self.command == Protocol.responseCommand

    @property
    def isConnect(self) -> bool:
        return self.command == Protocol.connectCommand

    @property
    def asJsonStr(self) -> str:
        return json.dumps(self.asJson)

    @property
    def asJson(self) -> dict:
        return {
            'command': self.command,
            'msgId': self.msgId,
            'messages': self.messages,
            'payload': self.payload,
            'raw': self.raw}

    def __str__(self):
        return (
            f'FromServerMessage(\n'
            f'\tcommand={self.command},\n'
            f'\tmsgId={self.msgId},\n'
            f'\tmessages={self.messages},\n'
            f'\tpayload={self.payload},\n'
            f'\traw={self.raw})')
