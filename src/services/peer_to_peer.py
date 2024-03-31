#------------------------------------------------------------------
# COS IW
# peer_to_peer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
# from utils import socket_utils
from threading import Thread
import struct
import time

#------------------------------------------------------------------
# From stack overflow: https://stackoverflow.com/questions/53479668/how-to-make-2-clients-connect-each-other-directly-after-having-both-connected-a
def addr_to_bytes(addr):
    return socket.inet_aton(addr[0]) + struct.pack('H', addr[1])

def bytes_to_addr(addr):
    return (socket.inet_ntoa(addr[:4]), struct.unpack('H', addr[4:])[0])

def udp_client(addr):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            print('Sending packet to server at: {}:{}'.format(*addr))
            sock.sendto(b'a', (addr[0], addr[1]))
            data, _ = sock.recvfrom(6) # 4 bytes for ip, 2 for port
            print('Received data from server')
            peer = bytes_to_addr(data)
            print('Peer:', *peer)
            sock.sendto(b'hello', peer)
            data, addr = sock.recvfrom(1024)
            print('{}:{} says {}'.format(*addr, data))
        print('Closed socket')
    except Exception as ex:
         print(ex, file=sys.stderr)
         sys.exit(1)
    return peer

def get_peer_addr(server_addr):
    # Validate server_addr
    if not isinstance(server_addr, tuple) or len(server_addr) != 2:
        raise ValueError("server_addr must be a tuple (host, port)")
    
    host, port = server_addr
    if not isinstance(host, str) or not host:
        raise ValueError("Host must be a non-empty string")
    
    if not (isinstance(port, int) and 0 <= port <= 65535):
        raise ValueError("Port must be an integer between 0 and 65535")
    
    peer_addr = udp_client(server_addr)
    return peer_addr

def main():
    parser = argparse.ArgumentParser(description=(
    "Client for the registrar application"))
    parser.add_argument("host", help=(
    "the host on which the server is running"))
    parser.add_argument("port", type = int,
        metavar="[0-65535]",
        help="the port at which the server is listening")
    args = parser.parse_args()

    addr = (args.host, args.port)
    get_peer_addr(addr)

#------------------------------------------------------------------
if __name__ == '__main__':
    main()