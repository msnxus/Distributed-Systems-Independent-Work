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
from PyQt5.QtCore import QDir

#------------------------------------------------------------------
class FileData():

    def __init__(self, dir:QDir = None, init=False):
        self._data = []
        if init:
            self.init_host_files(dir)
        return
    
    def like(self, filename):
        for file in self._data:
            if file["name"] == filename:
                file["likes"] += 1
                break
        print("Added like to {}".format(filename))

    def unlike(self, filename):
        for file in self._data:
            if file["name"] == filename:
                file["likes"] -= 1
                break
        print("Removed like from {}".format(filename))

    def dislike(self, filename):
        for file in self._data:
            if file["name"] == filename:
                file["dislikes"] += 1
                break
        print("Added dislike to {}".format(filename))
    
    def undislike(self, filename):
        for file in self._data:
            if file["name"] == filename:
                file["dislikes"] -= 1
                break
        print("Removed dislike from {}".format(filename))

    def comment(self, user_id, filename, comment_text):
        for file in self._data:
            if file["name"] == filename:
                file["num_comments"] += 1
                file["comments"].append((user_id, comment_text))
                break

    
    # Return a deep copy of the data in file_data
    def get_data(self):
        return self._data.copy()
    
    def get_comments(self):
        return self._data.copy()['comments']
    
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
            file_comments = file['comments']
            other_file_comments_set = set(other_file['comments'])
            unique_comments = [comment for comment in file_comments if comment not in other_file_comments_set]
            diffed._data.append({'name':file['name'],
                                       'likes':file['likes'] - other_file['likes'],
                                       'dislikes':file['dislikes'] - other_file['dislikes'],
                                       'num_comments':file['num_comments'] - other_file['num_comments'],
                                       'comments':unique_comments})
        return diffed
    
    # Return a file_data object which is a concatanation of entries in this
    # file_data with another
    def update(self, other: file_data.FileData):
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
    def init_host_files(self, directory):
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
