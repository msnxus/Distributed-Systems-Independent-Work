#------------------------------------------------------------------
# COS IW
# file_viewer.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import PyQt5.QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


# sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
# from utils import gui_utils

#------------------------------------------------------------------
LIKE_TEXT = "Like"
UNLIKE_TEXT = "Unlike"
DISLIKE_TEXT = "Dislike"
UNDISLIKE_TEXT = "Undislike"
DOWNLOAD_TEXT = "Download"
POST_TEXT = "Post"
FILE_OPTIONS = {'txt', 'pdf', 'mp4', 'mov'}

def horizontal_spacer():
    return PyQt5.QtWidgets.QSpacerItem(0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding, PyQt5.QtWidgets.QSizePolicy.Minimum)

class FileViewer():
    # Initialize SQLite database connection and retrieve data
    def __init__(self, file, ishost = False, filepath = None, like_checked = False, dislike_checked = False):
        self._file = file
        self._layout = PyQt5.QtWidgets.QGridLayout()
        self._file_display = PyQt5.QtWidgets.QWidget()              # FILE VIEWING WIDGET?
        self._file_name = PyQt5.QtWidgets.QLabel(file['name'])
        self._comments_section = PyQt5.QtWidgets.QTableView()
        self._comments_section.setMinimumHeight(200)

        self._like_button = PyQt5.QtWidgets.QPushButton(LIKE_TEXT)
        self._like_button.setCheckable(True)
        if like_checked:
            self._like_button.setChecked(True)
            self._like_button.setText(UNLIKE_TEXT)
        self._like_button.setStyleSheet("QPushButton:checked { background-color: green; color: white; }"
                                  "QPushButton { background-color: grey; color: black; }")
        self._like_button.clicked.connect(self.toggle_like_button)
        self._dislike_button = PyQt5.QtWidgets.QPushButton(DISLIKE_TEXT)
        self._dislike_button.setCheckable(True)
        if dislike_checked:
            self._dislike_button.setChecked(True)
            self._dislike_button.setText(UNDISLIKE_TEXT)
        self._dislike_button.setStyleSheet("QPushButton:checked { background-color: green; color: white; }"
                                  "QPushButton { background-color: grey; color: black; }")
        self._dislike_button.clicked.connect(self.toggle_dislike_button)


        self._download_button = PyQt5.QtWidgets.QPushButton(DOWNLOAD_TEXT)
        self._comment_input = PyQt5.QtWidgets.QLineEdit()
        self._post_button = PyQt5.QtWidgets.QPushButton(POST_TEXT)
        self._model = QStandardItemModel()
        self.init_ui(file)

        self.init_file_display(ishost, filepath)

    def toggle_like_button(self):
        if self._like_button.isChecked():
            self._like_button.setText(UNLIKE_TEXT)
        else:
            self._like_button.setText(LIKE_TEXT)

    def toggle_dislike_button(self):
        if self._dislike_button.isChecked():
            self._dislike_button.setText(UNDISLIKE_TEXT)
        else:
            self._dislike_button.setText(DISLIKE_TEXT)
    
    def init_file_display(self, ishost: bool = False, filepath = None):
            options = FILE_OPTIONS
    
            filetype = None
            if '.' in self._file["name"]:
                filetype = self._file["name"].split('.')[-1].lower()

            if filetype in {'mp4', 'mov'}:
                from PyQt5.QtCore import QUrl
                
                # Initialize QVideoWidget and QMediaPlayer
                self._video_widget = QVideoWidget()
                self._video_widget.setMinimumSize(640, 480)  # Set a reasonable default size

                self._player = QMediaPlayer()
                self._player.setVideoOutput(self._video_widget)
                
                if ishost:
                    self._player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
                else:
                    self._player.setMedia(QMediaContent(QUrl("udp://@127.0.0.1:" + str(filepath))))
                
                # Here you can insert the FFmpeg subprocess or similar setup for streaming
                
                self._layout.addWidget(self._video_widget, 0, 0, 1, 4)
                # self._video_widget.show()
                self._player.play()  # Start playing automatically
                
            else:
                message = f"Files of type: \'.{filetype}\' can't be displayed"
                self._file_display = PyQt5.QtWidgets.QLabel(message)
                self._file_display.setAlignment(Qt.AlignCenter)
                self._layout.addWidget(self._file_display, 0, 0, 1, 4)
    
    def get_layout(self):
        return self._layout
    
    def get_download_button(self):
        return self._download_button
    
    def get_like_button(self):
        return self._like_button
    
    def get_dislike_button(self):
        return self._dislike_button
    
    def get_comment_input(self):
        return self._comment_input
    
    def get_post_button(self):
        return self._post_button
    
    def populate(self, comments):
        self._model.clear()
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
        self._comments_section.setWordWrap(True)

        self._comments_section.verticalHeader().setDefaultSectionSize(40)  # Set a larger default height
        # Set column widths
        self._comments_section.setColumnWidth(0, 150)  # User
        self._comments_section.horizontalHeader().setStretchLastSection(True)
    
    def get_filename(self):
        return self._file['name']
    
    def init_ui(self, file):
        # Add Widgets
        self._layout.addWidget(self._file_name, 1, 0)
        self._layout.addWidget(self._like_button, 1, 1)
        self._layout.addWidget(self._dislike_button, 1, 2)
        self._layout.addWidget(self._download_button, 1, 3)
        self._layout.addWidget(self._comments_section, 2, 0, 1, 4)
        self._comments_section.setModel(self._model)

        comments = file['comments']
        self.populate(comments)

        # Add spacers to the _layout
            # horizontal
        self._layout.addItem(horizontal_spacer(), 1, 0)

        # Add text input and post button to the layout
        self._layout.addWidget(self._comment_input, 3, 0, 1, 3)  # Span 3 columns
        self._layout.addWidget(self._post_button, 3, 3)

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
