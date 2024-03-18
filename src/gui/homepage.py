#------------------------------------------------------------------
# COS IW
# homepage.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import PyQt5
import PyQt5.QtWidgets
from utils import gui_utils

#------------------------------------------------------------------

CONNECT_LINE_TEXT = "Enter Password"
CONNECT_BUTTON_TEXT = "Join Session"
HOST_LINE_TEXT = "Set Password"
HOST_BUTTON_TEXT = "Host Session"

class HomePage():

    def __init__(self):
        self._connect_text = PyQt5.QtWidgets.QLineEdit()
        self._connect_button = PyQt5.QtWidgets.QPushButton(CONNECT_BUTTON_TEXT)
        self._host_text = PyQt5.QtWidgets.QLineEdit()
        self._host_button = PyQt5.QtWidgets.QPushButton(HOST_BUTTON_TEXT)
        self._layout = PyQt5.QtWidgets.QGridLayout()
        self.init_ui()
    
    # ret str
    def get_connect_text(self):
        return self._connect_text.text()

    def get_connect_button(self):
        return self._connect_button

    # ret str
    def get_host_text(self):
        return self._host_text.text()

    def get_host_button(self):
        return self._host_button
    
    def get_layout(self):
        return self._layout

    def init_ui(self):
        # Creating widgets
        self._connect_text.setPlaceholderText(CONNECT_LINE_TEXT)
        self._host_text.setPlaceholderText(HOST_LINE_TEXT)

        # Adding widgets to the _layout
        self._layout.addWidget(self._connect_text, 0, 1)
        self._layout.addWidget(self._connect_button, 1, 1)
        self._layout.addWidget(self._host_text, 0, 3)
        self._layout.addWidget(self._host_button, 1, 3)

        # Add spacers to the _layout
            # horizontal
        self._layout.addItem(gui_utils.horizontal_spacer(), 0, 0)
        self._layout.addItem(gui_utils.horizontal_spacer(), 0, 1)
        self._layout.addItem(gui_utils.horizontal_spacer(), 0, 2)
        self._layout.addItem(gui_utils.horizontal_spacer(), 0, 3)
        self._layout.addItem(gui_utils.horizontal_spacer(), 0, 4)

def main():
    # Unit tests
    return

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
