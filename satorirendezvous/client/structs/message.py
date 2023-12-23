from typing import Union
from satorilib import logging
from satorirendezvous.server.structs.protocol import ToClientProtocol
# TODO: we need to create a rest protocol that is straight json serializable.
# the custom | design was because we were using UDP, but we don't need to with
# our connection to and from the rendezvous server, just between the peers.


class FromServerMessage():
    ''' a strcuture describing a message from the server '''

    @staticmethod
    def fromBytes(data: bytes):
        logging.debug('fromBytes---: ', data, print='teal')
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

    @staticmethod
    def fromStr(data: str):
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

    def __str__(self):
        return (
            f'FromServerMessage(\n'
            f'\tcommand={self.command},\n'
            f'\tmsgId={self.msgId},\n'
            f'\tmessages={self.messages},\n'
            f'\tpayload={self.payload},\n'
            f'\traw={self.raw})')
