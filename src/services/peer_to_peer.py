#------------------------------------------------------------------
# COS IW
# peer_to_peer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
from utils import socket_utils
from threading import Thread

#------------------------------------------------------------------

def udp_client(addr, sock):
    print('Sending packet to server')
    sock.sendto(b'', (addr[0], addr[1])) # REPLACE WITH PARTICULAR KEY
    data, _ = sock.recvfrom(6)
    print('Received data from server')
    peer = socket_utils.bytes_to_addr(data)
    print('Peer:', *peer)

    Thread(target=sock.sendto, args=(b'hello', peer)).start()
    data, addr = sock.recvfrom(1024)
    print('{}:{} says {}'.format(*addr, data))

def send_socket_communication(addr):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            udp_client(addr, sock)
            print('Closing socket')
    except Exception as ex:
        print(ex)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description=(
    "Client for the registrar application"))
    parser.add_argument("host", help=(
    "the host on which the server is running"))
    parser.add_argument("port", type = int,
        metavar="[0-65535]",
        help="the port at which the server is listening")
    args = parser.parse_args()

    # server_addr = ('172.214.83.79', 4000) # the server's  public address + port
    addr = (args.host, args.port)
    send_socket_communication(addr)

#------------------------------------------------------------------
if __name__ == '__main__':
    main()