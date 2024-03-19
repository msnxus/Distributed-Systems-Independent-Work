#------------------------------------------------------------------
# COS IW
# cloud_server.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
import os

#------------------------------------------------------------------

def main():
    # Socket stuff
    parser = argparse.ArgumentParser(
        description="Server host for holepunching and offline storage")
    parser.add_argument("port", type = int,
                   metavar="[0-65535]",
                   help="the port at which the server should listen")

    args = parser.parse_args()

    try:
        port = int(args.port)
        server_sock = socket.socket()
        print('Opened server socket')
        if os.name != 'nt':
            server_sock.setsockopt(socket.SOL_SOCKET,
                                   socket.SO_REUSEADDR, 1)

        server_sock.bind(('', port))
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')
        while True:
            try:
                sock, _ = server_sock.accept()
                with sock:
                    print('Accepted connection, opened socket')
                    # DO SOMETHING ! 
            except Exception as ex:
                print(sys.argv[0] + ":", ex, file=sys.stderr)
                sys.exit(1)
            print('Closed socket')

    except Exception as ex:
        print(sys.argv[0] + ":", ex, file=sys.stderr)
        sys.exit(1)

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
