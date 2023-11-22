# how to use:
#   on one machine run:
#       python3 udp.py <other ip address> 5002 5003 True
#   on another machine across the internet run:
#       python3 udp.py <other ip address> 5003 5002 True
#   at the same time.
# now they can talk to each other directly.

import sys
import socket
import threading


def listen(sock):
    while True:
        data = sock.recv(1024)
        print('\rpeer: {}\n> '.format(data.decode()), end='')


def run(remoteIp, remotePort=5002, localPort=5001, myLocalIsTheirRemote=False):
    localPort = int(localPort)
    remotePort = int(remotePort)
    print('\ngot peer')
    print('  ip:          {}'.format(remoteIp))
    print('  localPort: {}'.format(localPort))
    print('  repotePort:   {}\n'.format(remotePort))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', localPort))
    sock.sendto(b'0', (remoteIp, remotePort))
    listener = threading.Thread(target=listen, args=[sock], daemon=True)
    listener.start()
    if not myLocalIsTheirRemote:
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock2.bind(('0.0.0.0', remotePort))
    while True:
        msg = input('> ')
        if not myLocalIsTheirRemote:
            sock2.sendto(msg.encode(), (remoteIp, localPort))
        else:
            sock.sendto(msg.encode(), (remoteIp, remotePort))


if __name__ == '__main__' and len(sys.argv) > 4:
    run(
        remoteIp=sys.argv[1],
        remotePort=sys.argv[2],
        localPort=sys.argv[3],
        myLocalIsTheirRemote=sys.argv[4],  # reversed?
    )
else:
    print('usage: python3 manual.py <remoteIp> <remotePort> <localPort> <myLocalIsTheirRemote>')
