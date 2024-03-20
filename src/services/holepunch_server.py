#------------------------------------------------------------------
# COS IW
# holepunch_server.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import socket
import struct
#from utils import socket_utils
from threading import Thread

#------------------------------------------------------------------
# From stack overflow: https://stackoverflow.com/questions/53479668/how-to-make-2-clients-connect-each-other-directly-after-having-both-connected-a
def addr_to_bytes(addr):
    return socket.inet_aton(addr[0]) + struct.pack('H', addr[1])

def bytes_to_addr(addr):
    return (socket.inet_ntoa(addr[:4]), struct.unpack('H', addr[4:])[0])

def udp_server(sock):
    _, client_a = sock.recvfrom(0)
    _, client_b = sock.recvfrom(0)
    sock.sendto(addr_to_bytes(client_b), client_a)
    sock.sendto(addr_to_bytes(client_a), client_b)

#------------------------------------------------------------------