#!/usr/bin/python

import argparse
import shelve
import yaml
import collections

CATALOGS = [
    "instances",
    "domains",
    "accounts",
    "websites"
]

class Database(collections.Mapping):
    def __init__(self, filename="db.shelve"):
        self._db = shelve.open(filename, writeback=True)

        for key in CATALOGS:
            self._db.setdefault(key, {})
        self._db["instances"].setdefault(None, {})
        self._db["instances"][None]["catalog"] = "instances"
        self._db["instances"][None].setdefault("services", {})

    def add(self, item):
        self._db.setdefault(item['catalog'], {})[item['id']] = item

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return iter(self._db)

    def __len__(self):
        return len(self._db)

    def __getitem__(self, key):
        return self._db[key]


class DatabaseCLI:
    def run(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()

        add = subparsers.add_parser('add', help="Initialize database.")
        add.set_defaults(command='add')
        add.add_argument('filename', help="YAML file")

        dump = subparsers.add_parser('dump', help="Initialize database.")
        dump.set_defaults(command='dump')

        options = parser.parse_args()

        with Database("db.shelve") as db:
            if options.command == 'add':
                with open(options.filename) as stream:
                    db.add(yaml.safe_load(stream))
            if options.command == 'dump':
                print(yaml.dump(dict(db)))
