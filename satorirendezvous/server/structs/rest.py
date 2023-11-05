class ToClientRestProtocol():
    ''' protocol for sending messages to the client over REST '''

    responseCommand: str = 'RESPONSE'
    connectCommand: str = 'CONNECT'

    @staticmethod
    def commands() -> list[str]:
        return [
            ToClientRestProtocol.responseCommand,
            ToClientRestProtocol.connectCommand]

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return cmd in ToClientRestProtocol.commands()
