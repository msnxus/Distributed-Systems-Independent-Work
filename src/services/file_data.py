#------------------------------------------------------------------
# COS IW
# file_data.py
# Author: Ryan Hoffman
#------------------------------------------------------------------

import sys
import argparse
import socket
sys.path.append('/Users/ryanfhoffman/Downloads/COS IW/src')
# from utils import socket_utils
from threading import Thread
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDir

#------------------------------------------------------------------
class FileData():

    def __init__(self, init=False):
        self._data = []
        if init: self.init_host_files()
        return
    
    def get_data(self):
        return self._data.copy()
    
    def clone(self):
        ret = FileData()
        ret._data = self._data.copy()
        return ret
    
    def diff(self, other):
        if other is None: return self
        diffed = FileData()

        for file in self._data:
            diffed._data.append({'name':file['name'],
                                       'likes':file['likes'] - other['likes'],
                                       'dislikes':file['dislikes'] - other['dislikes'],
                                       'num_comments':file['num_comments'] - other['num_comments'],
                                       'comments':[comment for comment in file['comments'] if comment not in other['comments']]})
        return diffed
    
    def update(self, other):
        if other is None: return self
        updated = FileData()

        for file in self._data:
            updated._data.append({'name':file['name'],
                                       'likes':file['likes'] + other['likes'],
                                       'dislikes':file['dislikes'] + other['dislikes'],
                                       'num_comments':file['num_comments'] + other['num_comments'],
                                       'comments':file['comments'] + other['comments']})
        return updated
    
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
