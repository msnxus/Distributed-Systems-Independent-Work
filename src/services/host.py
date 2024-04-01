#------------------------------------------------------------------
# COS IW
# host.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src/services')
# from utils import socket_utils
from threading import Thread
import peer_to_peer
from PyQt5.QtCore import QObject, pyqtSignal
import params
import time

#------------------------------------------------------------------

class Host(QObject):
    _new_peer = pyqtSignal(tuple)

    def __init__(self, server_addr):
        super().__init__()
        self._peers = []
        self._server_addr = server_addr

        Thread(target=self.search_for_peers).start()
        return
    
    def add_peer(self, peer_addr):
        self._peers.append(peer_addr)

    def get_peers(self):
        return self._peers
    
    def init_cloud_server(self):
        # Send cloud server suggested p2p port on its dedicated listening port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                print('Sending cloud init port to server at: {}:{}'.format(params.SERVER_IP, params.PORT))
                sock.sendto(self._server_addr[1].to_bytes(4), (params.SERVER_IP, params.PORT))
        except Exception as ex:
                print(ex, file=sys.stderr)
                sys.exit(1)

    def search_for_peers(self):
            while(True):
                self.init_cloud_server()
                print('Waiting 2 seconds to send host packet')
                time.sleep(2) # Gives server time to open the p2p port before trying to discover peers on it
                try:
                    client_addr = peer_to_peer.get_peer_addr(self._server_addr)
                    self._new_peer.emit(client_addr)
                except Exception as ex:
                    print(ex, file=sys.stderr)

#------------------------------------------------------------------
