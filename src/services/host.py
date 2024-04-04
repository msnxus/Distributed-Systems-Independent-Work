#------------------------------------------------------------------
# COS IW
# host.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
from threading import Thread
import peer_to_peer
from PyQt5.QtCore import QObject, pyqtSignal
import params
import time
import file_data
import pickle

#------------------------------------------------------------------
class Host(QObject):
    _new_peer = pyqtSignal(list)

    # Get list of accepted peers
    def get_peers(self):
        return self._peers
    
    # Get FileData
    def get_data(self):
        return self._data

#------------------------------------------------------------------
#   Initialization
#------------------------------------------------------------------

    # Creates instance variables, pings cloud server to open correct P2P port
    # Starts peer searching thread and collects filedata via user input
    def __init__(self, server_addr):
        super().__init__()
        self._peers = []
        self._server_addr = server_addr
        self.init_cloud_server()
        print('Waiting {} seconds to send peer discovery packet'.format(params.LATENCY_BUFFER))
        time.sleep(params.LATENCY_BUFFER) # Gives server time to open the p2p port before trying to discover peers on it
        Thread(target=self.search_for_peers).start()
        self._data = file_data.FileData(init=True)
        return

    # Sends message to cloud server on static port in order to communicate
    # which p2p port should be opened to listen for peers on
    def init_cloud_server(self):
        # Send cloud server suggested p2p port on its dedicated listening port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                print('Sending cloud init port to server at: {}:{}'.format(params.SERVER_IP, params.PORT))
                sock.sendto(self._server_addr[1].to_bytes(4), (params.SERVER_IP, params.PORT))
        except Exception as ex:
                print(ex, file=sys.stderr)
                sys.exit(1)

#------------------------------------------------------------------
#   Peer matching THREAD
#------------------------------------------------------------------

    # Searches for peers using peer_to_peer module, emits signal upon new client
    # then can accept or reject in app.py flow
    def search_for_peers(self):
            while(True):
                try:
                    client_addr, sock = peer_to_peer.get_peer_addr(self._server_addr)
                    self._new_peer.emit([client_addr, sock])
                    time.sleep(params.LATENCY_BUFFER) # Gives server time to reopen peer discovery port
                except Exception as ex:
                    print(ex, file=sys.stderr)
    
    # Send message to peer indicating rejection
    def reject_peer(self, peer_addr, sock: socket.socket):
        sock.sendto(bytes('rejected', 'utf-8'), peer_addr)
    
    # Send message to peer indicating acceptance, add peer + sock to list
    def add_peer(self, peer_addr, sock: socket.socket):
        self._peers.append(peer_addr)
        sock.sendto(bytes('accepted', 'utf-8'), peer_addr)
        Thread(target=self.sync_with_peer, args=[peer_addr, sock]).start()

#------------------------------------------------------------------
#   Peer data syncing THREAD
#------------------------------------------------------------------
    
    # Listen to peer loop. Accepts input on peer socket, discards if addr
    # Doesn't match expected address for that port
    def sync_with_peer(self, peer_addr, sock: socket.socket):
        while(True):
            data, addr = sock.recvfrom(4096)
            if addr != peer_addr: continue
            else:
                print("Received data from peer: {}:{}".format(*peer_addr))
                sync_request = self.load_file_data_from_client(data)
                if sync_request is not None:
                    self._data = self._data.update(sync_request) # given diffed data, append to host
                    self.send_file_data(peer_addr, sock) # send back the updated copy to client
    
    # Unpickles received data, and returns it if possible
    def load_file_data_from_client(self, data):
        try:
            sync_request = pickle.loads(data)
            print("Successfully unpickled received data")
            return sync_request
        except pickle.UnpicklingError as e:
            print(f"Error unpickling received data: {e}")
            return None

    # Sends file data to client
    def send_file_data(self, peer_addr, sock: socket.socket):
        try:
            serialized_data = pickle.dumps(self._data)
            sock.sendto(serialized_data, peer_addr)
            print(f"Sent data to peer: {peer_addr[0]}:{peer_addr[1]}")
        except Exception as e:
            print(f"Error sending data to peer: {e}")

#------------------------------------------------------------------
