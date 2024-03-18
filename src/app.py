#------------------------------------------------------------------
# COS IW
# app.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import PyQt5
import PyQt5.QtWidgets
import sys
import gui.homepage

#------------------------------------------------------------------
#   Filespace
#------------------------------------------------------------------

#------------------------------------------------------------------
#   Homepage
#------------------------------------------------------------------
def connect_clicked_slot(password):
    print("connect with password %s" % password)
    return

def host_clicked_slot(password):
    print("host with password %s" % password)
    return

#------------------------------------------------------------------
#   Main
#------------------------------------------------------------------
def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)

    window = PyQt5.QtWidgets.QMainWindow()

    # Setup homepage + connect buttons to slots
    homepage = gui.homepage.HomePage()
    homepage.get_connect_button().clicked.connect(
        lambda: connect_clicked_slot(homepage.get_connect_text()))    
    homepage.get_host_button().clicked.connect(
        lambda: host_clicked_slot(homepage.get_host_text()))

    frame = PyQt5.QtWidgets.QFrame()
    frame.setLayout(homepage.get_layout())

    window.setCentralWidget(frame)
    screen_size = PyQt5.QtWidgets.QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)
    window.setWindowTitle("Princeton University Class Search")          # FIX THIS TEXT !
    window.show()

    sys.exit(app.exec_())

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
