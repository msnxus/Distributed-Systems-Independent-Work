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
import params
import time
from threading import Thread

#------------------------------------------------------------------
def addr_to_bytes(addr):
    return socket.inet_aton(addr[0]) + struct.pack('H', addr[1])

# def tcp_server():
#         p = params.TCP_PORT
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
#             print('[{}] Opened TCP socket'.format(p))
#             server_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
#             server_sock.bind(('0.0.0.0', p))
#             print('[{}] Bound TCP socket to port at: {}:{}'.format(p, *server_sock.getsockname()))
#         try:
#             server_sock.listen()
#             _, host = server_sock.accept()
#             print('[{}] Accepted connection from host at: {}:{}'.format(p, *host))
#             server_sock.listen()
#             _, client = server_sock.accept()
#             print('[{}] Received confirmation from client at: {}:{}'.format(p, *client))
#             print('[{}] Sending addresses to peers'.format(p))
#             server_sock.sendto(addr_to_bytes(client), host)
#             server_sock.sendto(addr_to_bytes(host), client)
#         except Exception as ex:
#                 print(sys.argv[0] + ":", ex, file=sys.stderr)
#                 return
#         print('[{}] Address swap complete'.format(p))

# On the specified port, waits for input from two users (first is host, second client)
# Sends addresses to each other then closes
def udp_server(p2p_port, sock: socket.socket):
    try:
        _, host = sock.recvfrom(1)
        print('[{}] Received confirmation from host at: {}:{}'.format(p2p_port, *host))
        _, client = sock.recvfrom(1)
        print('[{}] Received confirmation from client at: {}:{}'.format(p2p_port, *client))

        print('[{}] Sending addresses to peers'.format(p2p_port))
        sock.sendto(addr_to_bytes(client), host)
        sock.sendto(addr_to_bytes(host), client)
    except Exception as ex:
            print(sys.argv[0] + ":", ex, file=sys.stderr)
            return
    print('[{}] Address swap complete'.format(p2p_port))

# Opens port specified by host via password. Continues to listen for peer matching
# on that port infinitely
def open_host(p2p_port):
    while(True):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_sock:
                print('[{}] Opened server socket'.format(p2p_port))
                if os.name != 'nt':
                    server_sock.setsockopt(socket.SOL_SOCKET,
                                        socket.SO_REUSEADDR, 1)
                server_sock.bind(('0.0.0.0', p2p_port))
                print('[{}] Bound server socket to port at: {}:{}'.format(p2p_port, *server_sock.getsockname()))
                udp_server(p2p_port, server_sock) # For UDP protocol, no need to socket.listen / accept
            print('[{}] Closed server socket'.format(p2p_port))

        except Exception as ex:
            print(sys.argv[0] + ":", ex, file=sys.stderr)
            sys.exit(1)

def main():
    # Starts cloud server. Listens on params.PORT for new hosts
    while(True):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cloud_sock:
                print('[CLOUD] Initialized cloud listening socket')
                if os.name != 'nt':
                    cloud_sock.setsockopt(socket.SOL_SOCKET,
                                        socket.SO_REUSEADDR, 1)
                cloud_sock.bind(('0.0.0.0', params.PORT))
                print('[CLOUD] Bound cloud listening socket to port at: {}:{}'.format(*cloud_sock.getsockname()))
    # Receives port suggestion from host, opens that port to facilitate p2p
                try:
                    p2p_port, host = cloud_sock.recvfrom(4)
                    p2p_port = int.from_bytes(p2p_port, 'big')
                    print('[CLOUD] Received P2P port: {} from host at: {}:{}'.format(p2p_port, *host))
                except Exception as ex:
                        print(sys.argv[0] + ":", ex, file=sys.stderr)
                        return
    # Starts new p2p connection thread which will remain open indefinitely
                # if p2p_port == params.TCP_PORT: tcp_server()
                # else: Thread(target=open_host, args=[p2p_port]).start()
                Thread(target=open_host, args=[p2p_port]).start()
            print('[CLOUD] Closed cloud socket')

        except Exception as ex:
            print(sys.argv[0] + ":", ex, file=sys.stderr)
            sys.exit(1)

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
