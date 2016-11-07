#!/usr/bin/python

import os
import argparse
import shutil
import errno

def deploy(rootdir, destdir, filesystem=False):
    for entry in os.listdir(rootdir):
        if os.path.isdir(os.path.join(rootdir, entry)):
            deploy(
                os.path.join(rootdir, entry),
                os.path.join(destdir, entry) if filesystem else destdir,
                filesystem=True)
        else:
            print(os.path.join(rootdir, entry) + ' -> ' + os.path.join(destdir, entry))
            try:
                os.makedirs(destdir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            shutil.copy(os.path.join(rootdir, entry), os.path.join(destdir, entry))


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('destdir', help="destination directory")
    parser.add_argument('--srcdir', help="source directory", default="output")
    options = parser.parse_args()

    deploy(options.srcdir, options.destdir)
