import sys
import socket
import threading
# 138.199.6.207
# 65.130.251.139


def listen(sock):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind(('0.0.0.0', localPort))
    while True:
        data = sock.recv(1024)
        print('\rpeer: {}\n> '.format(data.decode()), end='')


def run(remoteIp='97.117.28.178', remotePort=50002, localPort=50001):
    localPort = int(localPort)
    remotePort = int(remotePort)
    print('\ngot peer')
    print('  ip:          {}'.format(remoteIp))
    print('  localPort: {}'.format(localPort))
    print('  repotePort:   {}\n'.format(remotePort))

    # punch hole
    # equiv: echo 'punch hole' | nc -u -p 20001 x.x.x.x 50002
    print('setting up socket')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', localPort))

    print('punching hole')
    sock.sendto(b'0', (remoteIp, remotePort))

    # listen for
    # equiv: nc -u -l 20001
    listener = threading.Thread(target=listen, args=[sock], daemon=True)
    listener.start()

    # send messages
    # equiv: echo 'xxx' | nc -u -p 50002 x.x.x.x 20001
    print('ready to exchange messages\n')
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.bind(('0.0.0.0', remotePort))

    while True:
        msg = input('> ')
        sock2.sendto(msg.encode(), (remoteIp, localPort))
        # sock.sendto(msg.encode(), (remoteIp, remotePort))


if __name__ == '__main__' and len(sys.argv) > 3:
    run(remoteIp=sys.argv[1], localPort=sys.argv[2], remotePort=sys.argv[3])
else:
    print('usage: python3 manual.py <remoteIp> <remotePort> <localPort>')
