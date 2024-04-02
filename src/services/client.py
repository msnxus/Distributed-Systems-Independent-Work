#------------------------------------------------------------------
# COS IW
# client.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
# sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
# from utils import socket_utils
from threading import Thread
import struct
import peer_to_peer
import pickle
import file_data # CANT BE FOUND NORMALLY

#------------------------------------------------------------------
class Client():

    def __init__(self, server_addr):
        host_addr, sock = peer_to_peer.get_peer_addr(server_addr)
        self._host_addr = host_addr #if connection was a success, still needs implementing
        self._sock = sock
        self._data = file_data.FileData()
        self._host_data = None

        self._success = self.attempt_connection()

        if self.successful_connection: self.sync_host()
        else: self._sock.close()

    def successful_connection(self):
        return self._success
    
    def get_data(self):
        return self._data
    
    def attempt_connection(self):
        while(True):
            data, _ = self.recv_host()
            if 'accepted' in data.decode('utf-8'):
                print('Accepted by host')
                return True
            elif 'rejected' in data.decode('utf-8'): 
                print('Rejected by host')
                return False
    
    def recv_host(self):
        while(True):
                data, addr = self._sock.recvfrom(4096)
                if addr == self._host_addr: break
        return data, addr
    
    def sync_host(self):
        try:
            diffed = self._data.diff(self._host_data)
            serialized_data = pickle.dumps(diffed)
            
            self._sock.sendto(serialized_data, self._host_addr)
            print(f"Sent data to host: {self._host_addr[0]}:{self._host_addr[1]}")
            data, addr = self.recv_host()
            print("Received data from host: {}:{}".format(*addr))
            self._data = pickle.loads(data)
            self._host_data = self._data.clone()
        except Exception as e:
            print(f"Error sending data to peer: {e}")


#------------------------------------------------------------------
