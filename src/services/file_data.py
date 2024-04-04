#------------------------------------------------------------------
# COS IW
# file_data.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
import file_data
from threading import Thread
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir

#------------------------------------------------------------------
class FileData():

    def __init__(self, init=False):
        self._data = []
        if init: self.init_host_files()
        return
    
    # Return a deep copy of the data in file_data
    def get_data(self):
        return self._data.copy()
    
    # Return a deep copy of the file_data object
    def clone(self):
        ret = FileData()
        ret._data = self._data.copy()
        return ret
    
    # Return a file_data object which is only the different entries in this
    # file_data compared to another
    def diff(self, other):
        if other is None: return self
        diffed = FileData()

        for index, file in enumerate(self._data):
            other_file = other.get_data()[index]
            diffed._data.append({'name':file['name'],
                                       'likes':file['likes'] - other_file['likes'],
                                       'dislikes':file['dislikes'] - other_file['dislikes'],
                                       'num_comments':file['num_comments'] - other_file['num_comments'],
                                       'comments':[comment for comment in file['comments'] if comment not in other_file['comments']]})
        return diffed
    
    # Return a file_data object which is a concatanation of entries in this
    # file_data with another
    def update(self, other: file_data):
        if other is None or other.is_empty(): return self
        updated = FileData()

        for index, file in enumerate(self._data):
            other_file = other.get_data()[index]
            updated._data.append({'name':file['name'],
                                       'likes':file['likes'] + other_file['likes'],
                                       'dislikes':file['dislikes'] + other_file['dislikes'],
                                       'num_comments':file['num_comments'] + other_file['num_comments'],
                                       'comments':file['comments'] + other_file['comments']})
        return updated
    
    # Return if there is data entered into the file_data
    def is_empty(self):
        return len(self._data) == 0
    
    # Prompt host for a directory, fill in files based on existing files in this
    # Directory (Not including other directories)
    def init_host_files(self):
        directory = QFileDialog.getExistingDirectory(None, "Select Directory")
        if directory is not None:
            dir = QDir(directory)
            dir.setFilter(QDir.Files | QDir.NoDotAndDotDot)
            files = dir.entryList()

            for file in files:
                self._data.append({'name':file,
                                       'likes':0,
                                       'dislikes':0,
                                       'num_comments':0,
                                       'comments':[]})

            


#------------------------------------------------------------------
