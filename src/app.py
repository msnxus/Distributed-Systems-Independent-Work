#------------------------------------------------------------------
# COS IW
# app.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import PyQt5
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QMessageBox
import sys
import gui.homepage
import gui.file_space
import gui.file_viewer
from services import params
import services.host, services.client
import time
from threading import Thread
from services import file_data
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QDialog, QLineEdit

#------------------------------------------------------------------
#   Instance variables
#------------------------------------------------------------------
_window = None
_filespace = None
user = None

def is_host():
    return isinstance(user, services.host.Host)

#------------------------------------------------------------------
#   File Viewer
#------------------------------------------------------------------
def initialize_fileviewer(index,
                          file_data: file_data.FileData):
    global user
    global _filespace

    i = index.sibling(index.row(), 0)
    filename = _filespace.get_model().data(i)
                                        
    for f in file_data.get_data():
        if f['name'] == filename:
            file = f

    filepath = None
    if is_host():
        filepath = user.get_dir() + '/' + file['name']
    else:
        filepath = user.get_client_port()
        #user.stream_from_host(file['name'])
    
    fileviewer = gui.file_viewer.FileViewer(file, is_host(), filepath, user.is_liked(file["name"]), user.is_disliked(file["name"]))

    fileviewer.get_download_button().clicked.connect(
        lambda: handle_download(fileviewer.get_filename()))
    
    fileviewer.get_like_button().clicked.connect(
        lambda: handle_like(fileviewer.get_filename()))
    
    fileviewer.get_dislike_button().clicked.connect(
        lambda: handle_dislike(fileviewer.get_filename()))
    
    fileviewer.get_post_button().clicked.connect(
        lambda: handle_comment(fileviewer, fileviewer.get_comment_input()))

    # Create a QDialog to act as a window
    window = QDialog(parent=_window)
    window.resize(_window.size())
    window.setWindowTitle("File Viewer")
    
    window.setLayout(fileviewer.get_layout())
    
    # Show the window
    window.show()
    return window  # keep it alive?

def handle_download(filename):
    if is_host():
        print("Can't download as host")
    else:
        user.download_from_host(filename)

def handle_like(filename):
    global _filespace
    user.add_like(filename)
    _filespace.populate(user.get_data())

def handle_dislike(filename):
    global _filespace
    user.add_dislike(filename)
    _filespace.populate(user.get_data())

def handle_comment(fileviewer: gui.file_viewer.FileViewer, comment_text_input: QLineEdit):
    global _filespace
    comment_text = comment_text_input.text()
    comment_text_input.clear()

    if comment_text != '':
        user.add_comment(fileviewer.get_filename(), comment_text)
        _filespace.populate(user.get_data())
        fileviewer.populate(user.get_comments(fileviewer.get_filename()))
        print("Added comment to {}".format(fileviewer.get_filename()))
    

#------------------------------------------------------------------
#   File Space
#------------------------------------------------------------------

# Sets up new filespace based on the given data, and displays it in the window
# Connects filespace doubleclicked slot
def initialize_filespace(file_data: file_data.FileData):
    global _filespace
    _filespace = gui.file_space.FileSpace()
    frame = PyQt5.QtWidgets.QFrame()
    frame.setLayout(_filespace.get_layout())
    _window.setCentralWidget(frame)
    _window.setWindowTitle("File Space")

    _filespace.populate(file_data)

    _filespace.get_table().clicked.connect(lambda index: initialize_fileviewer(index, user.get_data()))

    _filespace.get_sync_button().clicked.connect(handle_sync)

    #if not is_host(): collect_eval_data()

def handle_sync():
    if is_host():
        print("Can't sync as host")
    else:
        user.sync_host()
    _filespace.populate(user.get_data())

def collect_eval_data():
    for file in user.get_data().get_data():
        user.download_from_host(file['name'])

#------------------------------------------------------------------
#   Homepage
#------------------------------------------------------------------

# Translates alphanumeric password into number between 10005 to 65000 inclusive
# This is the valid port range for peer to peer connection with the Cloud Matcher
def simple_hash(password):
    charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    if (len(password) < 1 or len(password) > 4):
        raise ValueError("Password must be 1 to 4 characters long")
    for char in password:
        if char not in charset: raise ValueError(f"Invalid character in password: '{char}'")
    
    base = 62
    hash_value = 0
    for char in password:
        hash_value = hash_value * base + charset.index(char)
    # Adjust the hash value to fit into the range of 10005 to 65000
    min_port = 10005
    max_port = 65000
    range_size = max_port - min_port + 1
    hash_value = (hash_value % range_size) + min_port
    return hash_value

# Slot to handle 'join' button clicked in main menu
# Initializes new client, connects to host session, and pulls host files into
# filespace
def client_clicked_slot(password):
    global user
    try:
        port = simple_hash(password)
    except Exception as ex:
        print(ex)
        return
    print("connect with password %s, which corresponds to port %d" % (password, port))
    
    client = services.client.Client((params.SERVER_IP, port))

    if client.successful_connection():
        user = client
        initialize_filespace(client.get_data())
    else:
        # Handle unsuccessful connection
        client_rejected(password)
        return
    return

# Slot to handle 'host' button clicked in main menu
# Initializes new host, connects to filespace, listens for peers
def host_clicked_slot(password):
    global user
    try:
        port = simple_hash(password)
    except Exception as ex:
        print(ex)
        return
    print("host with password %s, which corresponds to port %d" % (password, port))
    
    host = services.host.Host((params.SERVER_IP, port))
    user = host
    host._new_peer.connect(lambda args: peer_popup(host, args[0], args[1]))
    initialize_filespace(host.get_data())
    return

# Supplies a popup window asking if a host will accept a peer. If yes, adds to
# hosts list of peers.
def peer_popup(host: services.host.Host, client_addr, sock):
    reply = QMessageBox.question(None, 'New Peer Detected', 
                            f"Do you want to add this peer: {client_addr}?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No)
    if reply == QMessageBox.Yes:
        print("Host agreed to add peer.")
        host.add_peer(client_addr, sock)
    else:
        print("Host declined to add peer.")
        host.reject_peer(client_addr, sock)

def client_rejected(password: str):
    QMessageBox.critical(None, 'Connection Rejected', 
                         f"Host with password: {password} has rejected the connection request.",
                         QMessageBox.Ok)

#------------------------------------------------------------------
#   Main
#------------------------------------------------------------------
def main():
    # Run as: PYTHONPATH='services' python3 app.py
    global _window

    app = PyQt5.QtWidgets.QApplication(sys.argv)

    _window = PyQt5.QtWidgets.QMainWindow()

    # Setup homepage + connect buttons to slots
    homepage = gui.homepage.HomePage()
    homepage.get_connect_button().clicked.connect(
        lambda: client_clicked_slot(homepage.get_connect_text()))    
    homepage.get_host_button().clicked.connect(
        lambda: host_clicked_slot(homepage.get_host_text()))

    frame = PyQt5.QtWidgets.QFrame()
    frame.setLayout(homepage.get_layout())

    _window.setCentralWidget(frame)
    screen_size = PyQt5.QtWidgets.QDesktopWidget().screenGeometry()
    _window.resize(screen_size.width()//2, screen_size.height()//2)
    _window.setWindowTitle("Homepage")
    _window.show()

    sys.exit(app.exec_())

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
