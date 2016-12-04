#!/usr/bin/python

""" Miscellaneous helper functions """
import os

def run_without_exception(function, exc_type, condition=lambda e: True):
    def wrapper(*args, **kargs):
        try:
            function(*args, **kargs)
        except exc_type as e:
            if not condition(e):
                raise
    return wrapper

makedirs = run_without_exception(os.makedirs, OSError, lambda e: e.errno == 17)
symlink = run_without_exception(os.symlink, OSError, lambda e: e.errno == 17)
