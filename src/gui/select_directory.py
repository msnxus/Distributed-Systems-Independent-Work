#------------------------------------------------------------------
# COS IW
# select_directory.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import PyQt5
import PyQt5.QtWidgets

#------------------------------------------------------------------

class SelectDirectory():

    def __init__(self):
        self._layout = PyQt5.QtWidgets.QGridLayout
        self.init_ui()
    
    def get_layout(self):
        return self._layout

    def init_ui(self):
        # Setup a UI which is a directory picker
        return

def main():
    # Unit tests
    return

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
