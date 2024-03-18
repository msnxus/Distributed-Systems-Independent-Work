#------------------------------------------------------------------
# COS IW
# file_viewer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import PyQt5.QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem

sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
from utils import gui_utils

#------------------------------------------------------------------
class FileViewer():
    # Initialize SQLite database connection and retrieve data
    def __init__(self):
        self._layout = PyQt5.QtWidgets.QGridLayout()
        self._file_table = PyQt5.QtWidgets.QTableView()
        self._host_status = PyQt5.QtWidgets.QLabel()
        self._sync_button = PyQt5.QtWidgets.QPushButton()
        self._model = QStandardItemModel()
        self.init_ui()
    
    def get_layout(self):
        return self._layout
    
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
    fileviewer = FileViewer()
    frame.setLayout(fileviewer.get_layout())
    window.setCentralWidget(frame)
    window.show()
    sys.exit(app.exec_())

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
