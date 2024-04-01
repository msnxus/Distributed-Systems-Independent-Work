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
from services import params
import services.host, services.client
import time
from threading import Thread

#------------------------------------------------------------------
#   Instance variables
#------------------------------------------------------------------
_window = None
#------------------------------------------------------------------
#   Filespace
#------------------------------------------------------------------

#------------------------------------------------------------------
#   Homepage
#------------------------------------------------------------------

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

def connect_clicked_slot(password):
    try:
        port = simple_hash(password)
    except Exception as ex:
        print(ex)
        return
    print("connect with password %s, which corresponds to port %d" % (password, port))

    client = services.client.Client((params.SERVER_IP, port))

    return

def host_clicked_slot(password):
    try:
        port = simple_hash(password)
    except Exception as ex:
        print(ex)
        return
    print("host with password %s, which corresponds to port %d" % (password, port))
    
    host = services.host.Host((params.SERVER_IP, port))
    host._new_peer.connect(lambda args: peer_popup(host, args))
    
    filespace = gui.file_space.FileSpace()
    frame = PyQt5.QtWidgets.QFrame()
    frame.setLayout(filespace.get_layout())
    _window.setCentralWidget(frame)
    _window.setWindowTitle("File Space")
    filespace.init_host_files()
    return

def peer_popup(host, client_addr):
    reply = QMessageBox.question(None, 'New Peer Detected', 
                            f"Do you want to add this peer: {client_addr}?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No)
    if reply == QMessageBox.Yes:
        print("Host agreed to add peer.")
        host.add_peer(client_addr)
    else:
        print("Host declined to add peer.")

#------------------------------------------------------------------
#   Main
#------------------------------------------------------------------
def main():
    global _window

    app = PyQt5.QtWidgets.QApplication(sys.argv)

    _window = PyQt5.QtWidgets.QMainWindow()

    # Setup homepage + connect buttons to slots
    homepage = gui.homepage.HomePage()
    homepage.get_connect_button().clicked.connect(
        lambda: connect_clicked_slot(homepage.get_connect_text()))    
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
