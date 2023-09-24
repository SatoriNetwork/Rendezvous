import requests
from satorilib import logging
from satorirendezvous.client.structs.message import FromServerMessage
from satorirendezvous.client.structs.protocol import ToServerProtocol


class RendezvousByRest():
    ''' conn for restful server '''

    def __init__(
        self,
        host: str,
        timed: bool = True,
        onMessage: function = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.msgId = 0
        self.rendezvousServer = host
        self.timed = timed
        self.listen = True
        self.onMessage = onMessage or self.display
        self.inbox = []
        self.outbox = {}
        self.checkin()

    def display(self, msg, addr=None):
        logging.info(f'from: {addr}, {msg}', print=True)

    def send(self, cmd: str, msgs: list[str] = None):
        ''' compiles a payload including msgId, updates outbox, and sends '''
        if not ToServerProtocol.isValidCommand(cmd):
            logging.error('command not valid', cmd, print=True)
            return
        try:
            payload = ToServerProtocol.compile([
                x for x in [cmd, str(self.msgId), *(msgs or [])]
                if isinstance(x, int) or (x is not None and len(x) > 0)])
            self.outbox[self.msgId] = payload
        except Exception as e:
            logging.warning('err w/ payload', e, cmd, self.msgId, msgs)
        self.msgId += 1
        response = requests.post(self.rendezvousServer, data=payload)
        if response.status_code != 200 or not response.text.startswith('{"response": '):
            logging.warning('bad response', response, payload)
        for msg in response.json()['response']:
            message = FromServerMessage(msg)
            self.inbox.append(message)
            self.onMessage(message)

    def checkin(self):
        self.send(ToServerProtocol.checkinPrefix)
