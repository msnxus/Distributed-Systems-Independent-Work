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
from utils.socket_utils import bytes_to_addr
import params
import time
import pickle
import subprocess
import file_data # CANT BE FOUND NORMALLY

#------------------------------------------------------------------
class Client():

    def __init__(self, server_addr):
        host_addr, sock = peer_to_peer.get_peer_addr(server_addr)
        self._host_addr = host_addr #if connection was a success, still needs implementing
        self._sock = sock
        self._data = file_data.FileData()
        self._host_data = None
        self._liked = {}
        self._disliked = {}

        self._success = self.attempt_connection()

        if self.successful_connection: self.sync_host()
        else: self._sock.close()

    def get_client_port(self):
        return self._sock.getsockname()[1]

    def successful_connection(self):
        return self._success
    
    def get_data(self):
        return self._data
    
    # Get comments for a file
    def get_comments(self, filename):
        for f in self._data.get_data():
            if f['name'] == filename:
                comments = f['comments']
                break
        return comments
    
    def attempt_connection(self):
        while True:
            data, _ = self.recv_host()
            if 'accepted' in data.decode('utf-8'):
                print('Accepted by host')
                return True
            elif 'rejected' in data.decode('utf-8'): 
                print('Rejected by host')
                return False
    
    def recv_host(self):
        while(True):
                data, addr = self._sock.recvfrom(65535)
                if addr == self._host_addr: break
        return data, addr
    
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
        self._data.comment(self._sock.getsockname()[0], filename, comment_text)
    
    def sync_host(self):
        try:
            diffed = self._data.diff(self._host_data)
            serialized_data = pickle.dumps(diffed)
            self._sock.sendto(params.SYNC_REQUEST, self._host_addr)
            print('Sent sync request to host')
            time.sleep(0.5)
            self._sock.sendto(serialized_data, self._host_addr)
            print(f"Sent data to host: {self._host_addr[0]}:{self._host_addr[1]}")
            data, addr = self.recv_host()
            print("Received data from host: {}:{}".format(*addr))
            self._data = pickle.loads(data)
            self._host_data = self._data.clone()
        except Exception as e:
            print(f"Error sending data to peer: {e}")

    # adapted from: https://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python
    def download_from_host(self, file_name: str):
        self._sock.sendto(params.DOWNLOAD_REQUEST, self._host_addr)
        print('Sent download request to host')
        time.sleep(0.5)  # Giving the server time to process the request
        self._sock.sendto(bytes(file_name + "**__$$", encoding='utf-8'), self._host_addr)

        buf = 65535
        f = open(file_name, 'wb')

        time.sleep(1)  # Give the host time to be first to the server request
        tcp_sock = self.tcp_holepunch()

        try:
            tcp_sock.settimeout(5)  # Initial timeout for receiving the first packet
            while True:
                data = tcp_sock.recv(buf)
                f.write(data)
                tcp_sock.settimeout(1)  # Reset timeout after each packet received
        except socket.timeout:
            print("Timeout reached, no more data.")
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            f.close()
            tcp_sock.close()
            print("File downloaded or download stopped due to error.")

    # Connects to Cloud Matcher, sends packet to alert of its existence. Cloud Matcher
    # Will respond with peers addresses. Peers break NAT and say hello to each other.
    def tcp_holepunch(self):
        addr = (params.SERVER_IP,params.TCP_PORT)
        time.sleep(params.LATENCY_BUFFER)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print('[TCP] Connecting to server at: {}:{}'.format(*addr))
            sock.connect(addr)
            portUsed = sock.getsockname()[1]
            print('[TCP] Sent address to server')
            sock.close()
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock2.bind(('0.0.0.0', portUsed))
            sock2.listen()
            tcp_sock, host = sock2.accept()
            print('[TCP] Host:', *host)

            time.sleep(0.5)
        except Exception as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)
        return tcp_sock

    def stream_from_host(self, file_name: str):
        target_port = self._sock.getsockname()[1]

        self._sock.sendto(params.STREAM_REQUEST, self._host_addr)
        time.sleep(0.5)
        self._sock.sendto(bytes(file_name + "**__$$", encoding='utf-8'), self._host_addr)
        time.sleep(0.5)
        self.receive_and_play_video(target_port)
        

#------------------------------------------------------------------
#   Peer file streaming
#------------------------------------------------------------------

    def receive_and_play_video(self, target_port):
        command = [
            'ffplay',  # FFmpeg's media player utility
            '-i', f'udp://@:{target_port}',  # Input from UDP
            '-bufsize', '65535',  # Set buffer size
            '-infbuf',  # No buffer size limit, useful for live streams
            '-sync', 'video'  # Sync to video if audio is not present or important
        ]
        subprocess.run(command)


#------------------------------------------------------------------
