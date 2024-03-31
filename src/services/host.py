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

    def search_for_peers(self):
        while(True):
            try:
                client_addr = peer_to_peer.get_peer_addr(self._server_addr)
                self._new_peer.emit(client_addr)
            except Exception as ex:
                print(ex, file=sys.stderr)
                sys.exit(1)

#------------------------------------------------------------------
