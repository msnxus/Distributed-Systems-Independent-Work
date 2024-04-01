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
        connection = peer_to_peer.get_peer_addr(server_addr)
        self._host_addr = connection #if connection was a success, still needs implementing
        return

#------------------------------------------------------------------
