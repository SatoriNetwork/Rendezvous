class Protocol():
    '''
    basic functionality for protocols
    '''

    @staticmethod
    def toBytes(msg: str) -> bytes:
        return msg.encode()

    @staticmethod
    def fromBytes(msg: bytes) -> str:
        return msg.decode()

    @staticmethod
    def prefixes():
        return []

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return cmd in Protocol.prefixes()
