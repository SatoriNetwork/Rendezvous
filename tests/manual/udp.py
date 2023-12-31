# how to use:
#   on one machine run:
#       python3 udp.py <other ip address> 5002 5003 True
#   on another machine across the internet run:
#       python3 udp.py <other ip address> 5003 5002 True
#   at the same time.
# now they can talk to each other directly.

# to test within a container:
# docker run --rm -it --privileged -p 5002:5002/udp -p 5003:5003/udp -v .:/udp python:slim bash
# python /udp/udp.py <remoteIp> 5003 5002 True

# how to get the public ip address:
# docker run --rm -it --privileged --net=host --cap-add NET_ADMIN -v .:/udp python:slim bash
# apt-get update; apt-get install curl -y; curl https://satorinet.io/ip/

import sys
import time
import socket
import threading


class SimpleUDP():
    def __init__(self, remoteIp, remotePort=5002, localPort=5001, myLocalIsTheirRemote=False):
        self.remoteIp = remoteIp
        self.remotePort = int(remotePort)
        self.originalRemotePort = int(remotePort)
        self.localPort = int(localPort)
        self.myLocalIsTheirRemote = myLocalIsTheirRemote
        self.message = ''
        self.sock: socket.socket
        self.sock2: socket.socket
        self.run()
        self.send()

    def listen(self):
        self.sock.settimeout(5)
        while self.message != 'exit':
            try:
                data, addr = self.sock.recvfrom(1024)
                if addr[1] != self.remotePort:
                    self.remotePort = int(addr[1])
                    print(
                        f'\rremote port: {self.remotePort}, addr: {addr}\n', end='')
                    self.fire(f'{self.remotePort}')
                print(f'\rpeer ({addr}): {data.decode()}\n> ', end='')
            except socket.timeout:
                continue
            except Exception as e:
                print(e)
                break
        self.sock.close()

    def run(self):
        print('\ngot peer')
        print(f'  remoteIp:   {self.remoteIp}')
        print(f'  repotePort: {self.remotePort}')
        print(f'  localPort:  {self.localPort}')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.localPort))
        self.sock.sendto(b'0', (self.remoteIp, self.remotePort))
        listener = threading.Thread(target=self.listen, daemon=True)
        listener.start()
        if not self.myLocalIsTheirRemote:
            self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock2.bind(('0.0.0.0', self.remotePort))

    def send(self):
        while True:
            self.message = input('> ')
            self.fire(self.message)
            if self.message == 'exit':
                print('exiting, please wait')
                time.sleep(6)
                break

    def fire(self, msg: str):
        if not self.myLocalIsTheirRemote:
            self.sock2.sendto(
                msg.encode(), (self.remoteIp, self.localPort))
        else:
            self.sock.sendto(
                msg.encode(), (self.remoteIp, self.remotePort))


if __name__ == '__main__' and len(sys.argv) > 4:
    SimpleUDP(
        remoteIp=sys.argv[1],
        remotePort=sys.argv[2],
        localPort=sys.argv[3],
        myLocalIsTheirRemote=sys.argv[4],  # reversed?
    )
else:
    print('usage: python3 manual.py <remoteIp> <remotePort> <localPort> <myLocalIsTheirRemote>')


# after extensive testing the only seemingly robust solution is to punch the
# hole and communicate outside of docker. worked fine when the dockers were on
# linux machines, but on windows it was sometimes impossible to communicate.
# then considering things like vpns, it was even more difficult. And docker
# containers on windows can't communicate with each other at all. So. we'll
# simply run the udp connections outside of docker.
