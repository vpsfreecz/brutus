#!/usr/bin/python

import brutus.db

import os
import yaml

filename = "test.shelve"

if os.path.exists(filename):
    os.unlink(filename)
db = brutus.db.Database(filename)

def load_yaml(filename):
    with open(filename) as stream:
        return yaml.load(stream)

db.add(load_yaml("examples/domain.yaml"))
db.add(load_yaml("examples/account.yaml"))
print(yaml.dump(dict(db)))
