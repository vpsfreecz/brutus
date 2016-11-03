#!/usr/bin/python

import os
import jinja2
from collections import OrderedDict

registered_classes = []

def register(cls):
    registered_classes.append(cls)
    return cls


class Generate:
    def __init__(self, db, rootdir):
        self.db = db
        self.rootdir = rootdir


@register
class PostfixGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "postfix")
        filename = os.path.join(basedir, "domains")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as stream:
            for item in self.db["domains"].values():
                print("{id} none".format(**item), file=stream)


@register
class DovecotGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "dovecot")
        filename = os.path.join(basedir, "passwd")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as stream:
            for item in self.db["accounts"].values():
                if {"domain", "password"}.issubset(item.keys()):
                    print("{id}@{domain}:{{{password[scheme]}}}{password[data]}".format(**item), file=stream)


@register
class WebserverGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "webserver")
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
                filename = os.path.join(basedir, platform, item['id'] + ".conf")
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w") as stream:
                    output = template[platform].render(variables)
                    print(output, file=stream)


@register
class BindGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "bind")

        os.makedirs(basedir, exist_ok=True)
        for name, domain in sorted(self.db["domains"].items()):
            filename = os.path.join(basedir, name)
            services = domain["services"]

            if "dns" not in services:
                continue
            if not services["dns"]["enabled"]:
                continue
            with open(filename, "w") as stream:
                for name, data in sorted(services["dns"]["records"].items()):
                    for typ, values in sorted(data.items()):
                        for value in sorted(values):
                            self.add_rr(stream, typ, name, value)

    @staticmethod
    def add_rr(stream, typ, name, value):
        print("{name} {typ} {value}".format(**vars()), file=stream)


def generate_all(db, rootdir):
    for cls in registered_classes:
        cls(db, rootdir).generate()
