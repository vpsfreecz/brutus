#!/usr/bin/python

import os, shutil, glob, subprocess
import yaml

from brutus.db import Database
from brutus.generate import generate_all
from brutus import utils


tmpdir = "tmp"
filename = os.path.join(tmpdir, "test.pickle")
rootdir = os.path.join(tmpdir, "output")


def cleanup():
    try:
        os.remove(filename)
    except OSError:
        pass
    utils.makedirs(tmpdir)
    shutil.rmtree(rootdir, ignore_errors=True)
    utils.makedirs(rootdir)


def test_empty():
    cleanup()

    with Database(filename) as db:
        generate_all(db, rootdir)


def test_services():
    cleanup()

    with Database(filename) as db:
        for example in glob.glob("examples/*.yaml"):
            with open(example) as stream:
                db.add(yaml.load(stream))

        generate_all(db, rootdir, generate_keys=False)

    subprocess.check_call(["diff", "-ru", rootdir, "tests/output"])
