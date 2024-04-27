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
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog
import params
import time
import file_data
import pickle
import subprocess

#------------------------------------------------------------------
class Host(QObject):
    _new_peer = pyqtSignal(list)

    # Get list of accepted peers
    def get_peers(self):
        return self._peers
    
    # Get FileData
    def get_data(self):
        return self._data
    
    # Get comments for a file
    def get_comments(self, filename):
        for f in self._data.get_data(): # This project is incredibly humbling.
            if f['name'] == filename:
                comments = f['comments']
                break
        return comments
    
    def get_dir(self):
        return self._dir

#------------------------------------------------------------------
#   Initialization
#------------------------------------------------------------------

    # Creates instance variables, pings cloud server to open correct P2P port
    # Starts peer searching thread and collects filedata via user input
    def __init__(self, server_addr):
        super().__init__()
        self._peers = []
        self._liked = {}
        self._disliked = {}
        self._server_addr = server_addr
        self.init_cloud_server()
        print('Waiting {} seconds to send peer discovery packet'.format(params.LATENCY_BUFFER))
        time.sleep(params.LATENCY_BUFFER) # Gives server time to open the p2p port before trying to discover peers on it
        Thread(target=self.search_for_peers).start()
        self._dir = QFileDialog.getExistingDirectory(None, "Select Directory")
        self._data = file_data.FileData(self._dir, init=True)
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

    def is_liked(self, filename): return False if filename not in self._liked else self._liked[filename]
    def is_disliked(self, filename): return False if filename not in self._disliked else self._disliked[filename] 
    
    def add_like(self, filename):
        if filename not in self._liked or self._liked[filename] == False:
            self._liked[filename] = True
            self._data.like(filename)
        
        else:
            self._liked[filename] = False
            self._data.unlike(filename)
        
    def add_dislike(self, filename):
        if filename not in self._disliked or self._disliked[filename] == False:
            self._disliked[filename] = True
            self._data.dislike(filename)
        
        else:
            self._disliked[filename] = False
            self._data.undislike(filename)

    def add_comment(self, filename, comment_text):
        self._data.comment("Host", filename, comment_text)

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
        Thread(target=self.listen_peer, args=[peer_addr, sock]).start()

#------------------------------------------------------------------
#   Peer listening THREAD
#------------------------------------------------------------------

    def listen_peer(self, peer_addr, sock: socket.socket):
        while(True):
            data, addr = sock.recvfrom(4)
            if addr != peer_addr: continue
            print("Examining request from peer: {}:{}".format(*peer_addr))
    
            if data == params.SYNC_REQUEST:
                print('File sync requested')
                self.sync_with_peer(peer_addr, sock)

            elif data == params.DOWNLOAD_REQUEST:
                print('Download requested')
                self.upload_to_peer(peer_addr, sock)

            elif data == params.STREAM_REQUEST:
                print('Stream requested')
                # get filename and strip:
                data,addr = sock.recvfrom(1024)
                file_name = data.strip('**__$$'.encode())
                print("Request for file:",file_name.decode())

                src = self._dir + '/' + file_name.decode() # absolute filepath

                self.stream_video_with_ffmpeg(src, peer_addr)

            else:
                print('Unrecognized request type: {}'.format(data))

#------------------------------------------------------------------
#   Peer file streaming
#------------------------------------------------------------------

    def stream_video_with_ffmpeg(source_filename, target_ip, target_port):

        command = [
            'ffmpeg',
            '-re',  # Read input at native frame rate. Mainly used for simulation.
            '-i', source_filename,  # Input file
            '-c:v', 'libx264',  # Use the H.264 video codec
            '-f', 'mpegts',  # Use MPEG-TS format suitable for streaming
            f'udp://{target_ip}:{target_port}'  # Output to UDP
        ]
        subprocess.run(command)


#------------------------------------------------------------------
#   Peer file download
#------------------------------------------------------------------

    # adapted from: https://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python
    def upload_to_peer(self, peer_addr, sock: socket.socket):
        buf = 1024
        # get filename and strip:
        data,addr = sock.recvfrom(buf)
        file_name = data.strip('**__$$'.encode())
        print("Request for file:",file_name.decode())

        file_path = self._dir + '/' + file_name.decode()
        # Send the file to the peer
        f=open(file_path,"rb") # PROBABLY need directory being used
        data = f.read(buf)
        while (data):
            try:
                if(sock.sendto(data, peer_addr)):
                    print("sending ...")
                    data = f.read(buf)
            except Exception as e:
                print('Failed send')
                print(e, file=sys.stderr)
                return
        print('Finished send')
        f.close()

#------------------------------------------------------------------
#   Peer data syncing
#------------------------------------------------------------------

    # sync with peer. Accepts input on peer socket, discards if addr
    # Doesn't match expected address for that port
    def sync_with_peer(self, peer_addr, sock: socket.socket):
            data, addr = sock.recvfrom(65535)
            if addr != peer_addr: 
                    print('Error: Unrecognized peer tried to send file sync data')
                    return
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
