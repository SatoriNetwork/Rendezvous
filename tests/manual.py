import sys
import socket
import threading
# 146.70.134.122
# 65.130.251.139


def run(remoteIp='97.117.28.178', remotePort=50002, localPort=50001):

    localPort = int(localPort)
    remotePort = int(remotePort)
    print('\ngot peer')
    print('  ip:          {}'.format(remoteIp))
    print('  localPort: {}'.format(localPort))
    print('  repotePort:   {}\n'.format(remotePort))

    # punch hole
    # equiv: echo 'punch hole' | nc -u -p 20001 x.x.x.x 50002
    print('punching hole')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', localPort))
    sock.sendto(b'0', (remoteIp, remotePort))

    print('ready to exchange messages\n')

    # listen for
    # equiv: nc -u -l 20001

    def listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', localPort))
        while True:
            data = sock.recv(1024)
            print('\rpeer: {}\n> '.format(data.decode()), end='')

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    # send messages
    # equiv: echo 'xxx' | nc -u -p 50002 x.x.x.x 20001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', remotePort))

    while True:
        msg = input('> ')
        sock.sendto(msg.encode(), (remoteIp, localPort))


if __name__ == '__main__' and len(sys.argv) > 3:
    run(remoteIp=sys.argv[1], localPort=sys.argv[2], remotePort=sys.argv[3])
else:
    print('usage: python3 manual.py <remoteIp> <remotePort> <localPort>')