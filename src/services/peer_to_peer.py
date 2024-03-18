#------------------------------------------------------------------
# COS IW
# peer_to_peer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import socket
from utils import socket_utils
from threading import Thread

#------------------------------------------------------------------

def udp_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'', (host, port))
    data, _ = sock.recvfrom(6)
    peer = socket_utils.bytes_to_addr(data)
    print('peer:', *peer)

    Thread(target=sock.sendto, args=(b'hello', peer)).start()
    data, addr = sock.recvfrom(1024)
    print('{}:{} says {}'.format(*addr, data))

server_addr = ('172.214.83.79', 4000) # the server's  public address
udp_client(server_addr)

#------------------------------------------------------------------