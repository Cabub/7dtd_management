import pickle
from config import config
import os

""" This file will be used to interface with a permanent data store
"""

db_dir = config.get('db_dir', )


def save(obj, filename=None):
    if filename is None:
        filename = config.get('db_name')
        directory = config.get('db_dir')
    with open(os.path.join(directory, filename), 'wb') as fs:
        pickle.dump(obj, fs)


def load(filename=None):
    if filename is None:
        filename = config.get('db_name')
        directory = config.get('db_dir')
    with open(os.path.join(directory, filename), 'rb') as fs:
        obj = pickle.load(fs)
    return obj