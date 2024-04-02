#------------------------------------------------------------------
# COS IW
# file_viewer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import PyQt5.QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
from utils import gui_utils

#------------------------------------------------------------------
LIKE_TEXT = "Like"
DISLIKE_TEXT = "Dislike"
DOWNLOAD_TEXT = "Download"

class FileViewer():
    # Initialize SQLite database connection and retrieve data
    def __init__(self, comments):
        self._layout = PyQt5.QtWidgets.QGridLayout()
        self._file_display = PyQt5.QtWidgets.QWidget()              # FILE VIEWING WIDGET?
        self._file_name = PyQt5.QtWidgets.QLabel()
        self._comments_section = PyQt5.QtWidgets.QTableView()
        self._like_button = PyQt5.QtWidgets.QPushButton(LIKE_TEXT)
        self._dislike_button = PyQt5.QtWidgets.QPushButton(DISLIKE_TEXT)
        self._download_button = PyQt5.QtWidgets.QPushButton(DOWNLOAD_TEXT)
        self._model = QStandardItemModel()
        self.init_ui(comments)
    
    def get_layout(self):
        return self._layout
    
    def init_ui(self, comments):
        # Add Widgets
        self._layout.addWidget(self._file_display, 0, 0, 1, 4)
        self._layout.addWidget(self._file_name, 1, 0)
        self._layout.addWidget(self._like_button, 1, 1)
        self._layout.addWidget(self._dislike_button, 1, 2)
        self._layout.addWidget(self._download_button, 1, 3)
        self._layout.addWidget(self._comments_section, 2, 0, 1, 4)
        self._comments_section.setModel(self._model)

        # Populate the model with data
        self._model.setHorizontalHeaderLabels(["User", "Comment"])
        for row_idx, row_data in enumerate(comments):
            for col_idx, cell_data in enumerate(row_data):
                item = QStandardItem(str(cell_data))
                self._model.setItem(row_idx, col_idx, item)

        # Table
        self._comments_section.setSortingEnabled(True)
        self._comments_section.setSelectionBehavior(PyQt5.QtWidgets.QTableView.SelectRows)
        self._comments_section.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
        # Set column widths
        self._comments_section.setColumnWidth(0, 150)  # User
        self._comments_section.setColumnWidth(1, 400)   # Comment

        # Add spacers to the _layout
            # horizontal
        self._layout.addItem(gui_utils.horizontal_spacer(), 1, 0)
        

def main():
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    window = PyQt5.QtWidgets.QMainWindow()
    frame = PyQt5.QtWidgets.QFrame()
    comments = [
        ["127.0.0.1", "This file sucks!"],
        ["localhost", "I actually really like it"],
        ["128.92.0.108", "Guys lets be civil"],
        ["DaFoppishDandy", "Just purchased the most splendid perfume"]
    ]
    fileviewer = FileViewer(comments)
    frame.setLayout(fileviewer.get_layout())
    window.setCentralWidget(frame)
    screen_size = PyQt5.QtWidgets.QDesktopWidget().screenGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)
    window.show()
    sys.exit(app.exec_())

#------------------------------------------------------------------
if __name__ == '__main__':
    main()
