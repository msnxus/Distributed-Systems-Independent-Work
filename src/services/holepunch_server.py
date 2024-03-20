#------------------------------------------------------------------
# COS IW
# holepunch_server.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import socket
from utils import socket_utils
from threading import Thread

#------------------------------------------------------------------

def udp_server(sock):
    _, client_a = sock.recvfrom(0)
    _, client_b = sock.recvfrom(0)
    sock.sendto(socket_utils.addr_to_bytes(client_b), client_a)
    sock.sendto(socket_utils.addr_to_bytes(client_a), client_b)

#------------------------------------------------------------------