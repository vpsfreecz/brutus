#!/usr/bin/python

""" Miscellaneous helper functions """
import os


def makedirs(path):
    """Emulates os.makedirs(exist_ok=True)"""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17:
            raise
