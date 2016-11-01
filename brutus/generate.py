#!/usr/bin/python

import os

class PostfixGenerate:
    def __init__(self, db, rootdir="output"):
        self.db = db
        self.basedir =  os.path.join(rootdir, "postfix")

    def generate(self):
        filename = os.path.join(self.basedir, "domains")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as stream:
            for item in self.db["domains"].values():
                print("{id} none".format(**item), file=stream)


class DovecotGenerate:
    def __init__(self, db, rootdir="output"):
        self.db = db
        self.basedir =  os.path.join(rootdir, "dovecot")

    def generate(self):
        filename = os.path.join(self.basedir, "passwd")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as stream:
            for item in self.db["accounts"].values():
                if {"domain", "password"}.issubset(item.keys()):
                    print("{id}@{domain}:{{{password[scheme]}}}{password[data]}".format(**item), file=stream)


def generate_all(db):
    PostfixGenerate(db).generate()
    DovecotGenerate(db).generate()
