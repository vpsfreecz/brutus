#!/usr/bin/python

import os, shutil, subprocess
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
