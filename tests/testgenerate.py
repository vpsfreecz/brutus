#!/usr/bin/python

import os
import shutil
import subprocess
import yaml

from brutus.db import Database
from brutus.generate import generate_all

tmpdir = "tmp"
filename = os.path.join(tmpdir, "test.pickle")
rootdir = os.path.join(tmpdir, "output")


def cleanup():
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass
    shutil.rmtree(rootdir)
    os.makedirs(rootdir)


def test_empty():
    cleanup()

    with Database(filename) as db:
        generate_all(db, rootdir)


def test_services():
    cleanup()

    with Database(filename) as db:
        with open("examples/domain.yaml") as stream:
            db.add(yaml.load(stream))
        with open("examples/mailaccount.yaml") as stream:
            db.add(yaml.load(stream))
        with open("examples/website.yaml") as stream:
            db.add(yaml.load(stream))
        with open("examples/website-minimal.yaml") as stream:
            db.add(yaml.load(stream))

        generate_all(db, rootdir)

    subprocess.check_call(["diff", "-ru", rootdir, "tests/output"])
