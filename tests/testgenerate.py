#!/usr/bin/python

import os, shutil, subprocess
import yaml

from brutus.db import Database
from brutus.generate import *

tmpdir = "tmp"
filename = os.path.join(tmpdir, "test.pickle")
rootdir = os.path.join(tmpdir, "output")

def test_services():
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    os.makedirs(tmpdir)
    os.makedirs(rootdir)

    with Database(filename) as db:
        with open("examples/domain.yaml") as stream:
            db.add(yaml.load(stream))
        with open("examples/mailaccount.yaml") as stream:
            db.add(yaml.load(stream))

        PostfixGenerate(db, rootdir).generate()
        DovecotGenerate(db, rootdir).generate()

    subprocess.check_call(["diff", "-ru", "tmp/output", "tests/output"])
