#------------------------------------------------------------------
# COS IW
# holepunch_server.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import socket
from utils import socket_utils
from threading import Thread

#------------------------------------------------------------------

def udp_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(host, port)

    _, client_a = sock.recvfrom(0)
    _, client_b = sock.recvfrom(0)
    sock.sendto(socket_utils.addr_to_bytes(client_b), client_a)
    sock.sendto(socket_utils.addr_to_bytes(client_a), client_b)

addr = ('0.0.0.0', 4000)
udp_server(addr)

#------------------------------------------------------------------