#------------------------------------------------------------------
# COS IW
# file_space.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import PyQt5.QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem

sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
from utils import gui_utils

#------------------------------------------------------------------
SYNC_BUTTON_TEXT = "Sync"

class FileSpace():
    # Initialize SQLite database connection and retrieve data
    def __init__(self, data):
        self._layout = PyQt5.QtWidgets.QGridLayout()
        self._file_table = PyQt5.QtWidgets.QTableView()
        self._host_status = PyQt5.QtWidgets.QLabel()
        self._sync_button = PyQt5.QtWidgets.QPushButton(SYNC_BUTTON_TEXT)
        self._model = QStandardItemModel()
        self.init_ui(data)
    
    def get_layout(self):
        return self._layout
    
    # Should be passed as list of length 4
    def add_item(self, item):
        self._model.appendRow([QStandardItem(str(cell)) for cell in enumerate(item)])

    def set_host_status(self, text):
        self._host_status.setText(text)

    def get_sync_button(self):
        return self._sync_button

    def init_ui(self, data):
        # Add Widgets
        self._layout.addWidget(self._file_table, 0, 0, 1, 2)
        self._layout.addWidget(self._host_status, 1, 0)
        self._layout.addWidget(self._sync_button, 1, 1)
        self._file_table.setModel(self._model)

        # Populate the model with data
        self._model.setHorizontalHeaderLabels(["Filename", "Likes", "Dislikes", "Comments"])
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QStandardItem(str(cell_data))
                self._model.setItem(row_idx, col_idx, item)

        # Table
        self._file_table.setSortingEnabled(True)
        self._file_table.setSelectionBehavior(PyQt5.QtWidgets.QTableView.SelectRows)
        self._file_table.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
        # Set column widths
        self._file_table.setColumnWidth(0, 200)  # Filenames
        self._file_table.setColumnWidth(1, 70)   # Likes
        self._file_table.setColumnWidth(2, 70)   # Dislikes
        self._file_table.setColumnWidth(3, 70)   # Comments

        # Host status       
        self._host_status.setText('Host is offline')

        # Add spacers to the _layout
            # horizontal
        self._layout.addItem(gui_utils.horizontal_spacer(), 1, 0)
        

def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    window = PyQt5.QtWidgets.QMainWindow()
    frame = PyQt5.QtWidgets.QFrame()
    # Sample data
    data = [
        ["Scene_1_Take_2.mp4", 2, 1, 3],
        ["Scene_1_Take_1.mp4", 3, 0, 2],
        ["Scene_1_Take_3.mp4", 5, 0, 2],
        ["Scene_1_Take_4.mp4", 5, 0, 2]
    ]
    filespace = FileSpace(data)
    frame.setLayout(filespace.get_layout())
    window.setCentralWidget(frame)
    window.show()
    sys.exit(app.exec_())

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
