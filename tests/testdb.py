#!/usr/bin/python

from brutus.db import Database

import os
import yaml

def test_db():
    filename = "test.shelve"

    if os.path.exists(filename):
        os.unlink(filename)
    db = Database(filename)

    def load_yaml(filename):
        with open(filename) as stream:
            return yaml.load(stream)

    db.add(load_yaml("examples/domain.yaml"))
    db.add(load_yaml("examples/account.yaml"))
    print(yaml.dump(dict(db)))
