#------------------------------------------------------------------
# COS IW
# client.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
# from utils import socket_utils
from threading import Thread
import struct
import peer_to_peer

#------------------------------------------------------------------
class Client():

    def __init__(self, server_addr):
        self.host = []
        self._host_addr = peer_to_peer.get_peer_addr(server_addr)
        return

#------------------------------------------------------------------
