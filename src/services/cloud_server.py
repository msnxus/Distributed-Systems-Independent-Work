#------------------------------------------------------------------
# COS IW
# cloud_server.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
import os
import struct

#------------------------------------------------------------------
# From stack overflow: https://stackoverflow.com/questions/53479668/how-to-make-2-clients-connect-each-other-directly-after-having-both-connected-a
def addr_to_bytes(addr):
    return socket.inet_aton(addr[0]) + struct.pack('H', addr[1])

def bytes_to_addr(addr):
    return (socket.inet_ntoa(addr[:4]), struct.unpack('H', addr[4:])[0])

def udp_server(sock):
    try:
        _, host = sock.recvfrom(1)
        print('Received confirmation from host at: {}:{}'.format(*host))
        _, client = sock.recvfrom(1)
        print('Received confirmation from client at: {}:{}'.format(*client))
        print('Sending addresses to peers')
        sock.sendto(addr_to_bytes(client), host)
        sock.sendto(addr_to_bytes(host), client)
    except Exception as ex:
            print(sys.argv[0] + ":", ex, file=sys.stderr)
            return
    print('Address swap complete')

def main():
    # Socket stuff
    parser = argparse.ArgumentParser(
        description="Server host for holepunching and offline storage")
    parser.add_argument("port", type = int,
                   metavar="[0-65535]",
                   help="the port at which the server should listen")

    args = parser.parse_args()
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
            port = int(args.port)
            print('Opened server socket')
            if os.name != 'nt':
                server_sock.setsockopt(socket.SOL_SOCKET,
                                    socket.SO_REUSEADDR, 1)

            server_sock.bind(('0.0.0.0', port))
            print('Bound server socket to port at: {}'.format(server_sock.getsockname()))
            udp_server(server_sock) # For UDP protocol, no need to socket.listen / accept
        print('Closed socket')

    except Exception as ex:
        print(sys.argv[0] + ":", ex, file=sys.stderr)
        sys.exit(1)

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
