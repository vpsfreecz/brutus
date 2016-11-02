#!/usr/bin/python

import os
import jinja2
from collections import OrderedDict

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

class WebserverGenerate:
    def __init__(self, db, rootdir="output"):
        self.db = db
        self.basedir =  os.path.join(rootdir, "webserver")

    def generate(self):
        templateLoader = jinja2.FileSystemLoader(searchpath="templates/")
        templateEnv = jinja2.Environment(loader=templateLoader)

        platforms = [ 'nginx', 'apache' ];
        template = {};

        for platform in platforms:
            template[platform] = templateEnv.get_template(platform + '/site.conf')

        defaults = {
            "id": None,
            "name": None,
            "root": None,
            "tls": "letsencrypt",
            "tls_params": None,
            "php": "false",
            "headers": None,
            "locations": None,
        }

        for item in self.db["websites"].values():
            variables = defaults.copy()
            variables.update(item)

            # set defaults
            variables['id'] = variables['domain'] if variables['id'] is None else variables['id']
            variables['name'] = variables['id'] if variables['name'] is None else variables['name']
            variables['root'] = "/srv/www/" + variables['domain'] + "/" + variables['id'] + "/www" if variables['root'] is None else variables['root']

            # replace headers and fastcgi-params by their ordered version; for tests
            if variables['headers'] is not None:
                variables['headers'] = OrderedDict(sorted(variables['headers'].items(), key=lambda t: t[0]))
            if variables['locations'] is not None:
                for loc in variables['locations']:
                    if 'fastcgi_params' in loc:
                        loc['fastcgi_params'] = OrderedDict(sorted(loc['fastcgi_params'].items(), key=lambda t: t[0]))

            for platform in platforms:
                filename = os.path.join(self.basedir, platform, item['id'] + ".conf")
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w") as stream:
                    output = template[platform].render(variables)
                    print(output, file=stream)

def generate_all(db):
    PostfixGenerate(db).generate()
    DovecotGenerate(db).generate()
    WebserverGenerate(db).generate()
