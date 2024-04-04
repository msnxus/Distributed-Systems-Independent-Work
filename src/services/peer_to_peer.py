#------------------------------------------------------------------
# COS IW
# peer_to_peer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
from utils.socket_utils import bytes_to_addr
from threading import Thread
import struct

#------------------------------------------------------------------

# Connects to Cloud Matcher, sends packet to alert of its existence. Cloud Matcher
# Will respond with peers addresses. Peers break NAT and say hello to each other.
def udp_client(addr):
    try:
        # Client is assigned port number in some valid range by their NAT
        # provider (this range is unknown to anyone else). By communicating with
        # Cloud, we learn what this valid port / NAT assignment is and use it
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Sending packet to server at: {}:{}'.format(*addr))
        sock.sendto(b'a', (addr[0], addr[1]))
        data, _ = sock.recvfrom(6) # 4 bytes for ip, 2 for port
        print('Received data from server')
        peer = bytes_to_addr(data)
        print('Peer:', *peer)

        # Once we know opens ports, execute NAT breaking protocol:
        # 1) A ----> B, dropped by B's firewall. A now is open to B.
        # 2) B ----> A, B is now open to A
        # 3) A receives B's message
        # 4) A ----> B
        # 5) B receives A's message
        sock.sendto(bytes('hello', 'utf-8'), peer)
        data, addr = sock.recvfrom(5)
        sock.sendto(bytes('hello', 'utf-8'), peer)

        print('{}:{} says {}'.format(*addr, data.decode('utf-8')))
    except Exception as ex:
         print(ex, file=sys.stderr)
         sock.close()
         sys.exit(1)
    return peer, sock

# Ensures proper arguments and runs udp client
def get_peer_addr(server_addr):
    # Validate server_addr
    if not isinstance(server_addr, tuple) or len(server_addr) != 2:
        raise ValueError("server_addr must be a tuple (host, port)")
    
    host, port = server_addr
    if not isinstance(host, str) or not host:
        raise ValueError("Host must be a non-empty string")
    
    if not (isinstance(port, int) and 0 <= port <= 65535):
        raise ValueError("Port must be an integer between 0 and 65535")
    
    peer_addr, sock = udp_client(server_addr)
    return peer_addr, sock

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