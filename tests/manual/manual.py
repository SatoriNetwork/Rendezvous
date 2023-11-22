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
    # you bind a second one if you give each peer the same local and remote port
    # or you don't have to if you give them reverse ports
    # sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock2.bind(('0.0.0.0', remotePort))

    while True:
        msg = input('> ')
        # sock2.sendto(msg.encode(), (remoteIp, localPort))
        sock.sendto(msg.encode(), (remoteIp, remotePort))


if __name__ == '__main__' and len(sys.argv) > 3:
    run(remoteIp=sys.argv[1], localPort=sys.argv[2], remotePort=sys.argv[3])
else:
    print('usage: python3 manual.py <remoteIp> <remotePort> <localPort>')


# one thing we could do is this:
# https://chat.openai.com/share/b24e6db5-6c69-4fba-bde2-83f944e28c34
# possibly talk directly to the flask server
# import subprocess

# def add_firewall_rule(name, port):
#     try:
#         subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={name}", "dir=in", "action=allow", "protocol=TCP", f"localport={port}"], check=True)
#         print(f"Firewall rule '{name}' added for port {port}")
#     except subprocess.CalledProcessError as e:
#         print(f"Error adding firewall rule: {e}")

# add_firewall_rule("FlaskAppRule", 5000)

# C:\Windows\System32>pip install upnpclient
# C:\Windows\System32>python
# >>> import upnpclient
# >>> devices = upnpclient.discover()
# >>> router = devices[0]
# >>> for service in router.services:
# ...     print(service)
# ...
# >>> wan_ip_connection_service = router.services[-1]
# >>> wan_ip_connection_service.AddPortMapping(
# ...     NewRemoteHost="",  # Usually empty for a general rule
# ...     NewExternalPort=24601,  # The port you want to open
# ...     NewProtocol="TCP",  # Protocol: TCP or UDP
# ...     NewInternalPort=24601,  # Internal port (should match the external one)
# ...     NewInternalClient="192.168.0.9",  # The internal IP of the host machine
# ...     NewEnabled="1",
# ...     NewPortMappingDescription="Satori",  # A description for the rule
# ...     NewLeaseDuration=0  # Lease duration, 0 is typically permanent
# ... )
# {}


def add_firewall_rule(name: str = 'Satori', port: int = 24601):
    import subprocess
    try:
        subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule",
                       f"name={name}", "dir=in", "action=allow", "protocol=TCP", f"localport={port}"], check=True)
        print(f"Firewall rule '{name}' added for port {port}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding firewall rule: {e}")
        return False


def get_public_ip():

    def bySocketSimple():
        import socket
        return socket.gethostbyname(socket.gethostname())

    def bySocketComplex():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def byPublicService():
        from urllib.request import urlopen
        import re
        data = str(urlopen('http://checkip.dyndns.com/').read())
        return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)

    def bySatoriService():
        import requests
        r = requests.get('https://satorinet.io/ip/')
        english = 'Your IP address is: '
        if r.text.startswith(english):
            return r.text[len(english):]
        else:
            return '127.0.0.1'

    def byBestGuess():
        return '192.168.0.1'

    for func in [bySocketSimple, bySocketComplex, byPublicService, bySatoriService, byBestGuess]:
        ip = func()
        if not ip.startswith('127'):
            return ip


def add_NAT_rule(name: str = 'Satori', port: int = 24601):
    import upnpclient
    for device in upnpclient.discover():
        for service in device.services:
            try:
                result = service.AddPortMapping(
                    NewRemoteHost="",  # Usually empty for a general rule
                    NewExternalPort=port,  # The port you want to open
                    NewProtocol="TCP",  # Protocol: TCP or UDP
                    # Internal port (should match the external one)
                    NewInternalPort=port,
                    NewInternalClient=get_public_ip(),  # The internal IP of the host machine
                    NewEnabled="1",
                    NewPortMappingDescription=name,  # A description for the rule
                    NewLeaseDuration=0  # Lease duration, 0 is typically permanent
                )
                if result == {}:
                    print('success')
                    return True
            except Exception as _:
                print('-')
    return False

# we could run these from the installer/runner and if it fails set a flag to
# use the alternative method

# add_NAT_rule()
# add_firewall_rule()

# uninstaller should remove the rule:
def remove_NAT_rule(port: int = 24601):
    import upnpclient
    for device in upnpclient.discover():
        for service in device.services:
            try:
                result = service.DeletePortMapping(
                    NewRemoteHost="",  # Usually empty
                    NewExternalPort=port,  # The external port of the rule to delete
                    NewProtocol="TCP"  # The protocol of the rule (TCP or UDP)
                )
                if result == {}:
                    print('success')
                    return True
            except Exception as _:
                print('-')
    return False
