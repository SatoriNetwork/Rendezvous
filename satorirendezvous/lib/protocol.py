class Protocol():
    ''' basic functionality for protocols '''

    @staticmethod
    def toBytes(msg: str) -> bytes:
        if isinstance(msg, bytes):
            return msg
        else:
            msg = str(msg)
        return msg.encode()

    @staticmethod
    def fromBytes(msg: bytes) -> str:
        if isinstance(msg, str):
            return msg
        return msg.decode()

    @staticmethod
    def toStr(msg: bytes) -> str:
        if not isinstance(msg, str) and not isinstance(msg, bytes):
            return str(msg)
        return Protocol.fromBytes(msg)

    @staticmethod
    def prefixes():
        return []

    @staticmethod
    def isValidCommand(cmd: bytes) -> bool:
        return cmd in Protocol.prefixes()

    @staticmethod
    def compile(cmd, *args: str) -> bytes:
        return Protocol.toBytes('|'.join([Protocol.toStr(cmd), [Protocol.toStr(arg) for arg in args]]))
