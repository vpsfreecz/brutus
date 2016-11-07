#!/usr/bin/python

from __future__ import print_function

import os
import jinja2

registered_classes = []

def register(cls):
    registered_classes.append(cls)
    return cls


class Generate:
    def __init__(self, db, rootdir):
        self.db = db
        self.rootdir = rootdir

    def makedirs(self, path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != 17:
                raise


@register
class PostfixGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "postfix")
        filename = os.path.join(basedir, "domains")

        self.makedirs(os.path.dirname(filename))
        with open(filename, "w") as stream:
            for item in self.db["domains"].values():
                print("{id} none".format(**item), file=stream)


@register
class DovecotGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "dovecot")
        filename = os.path.join(basedir, "passwd")

        self.makedirs(os.path.dirname(filename))
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
            template[platform] = templateEnv.get_template(platform + '/site.conf.j2')

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

            for platform in platforms:
                filename = os.path.join(basedir, platform, 'conf.d',  item['id'] + ".conf")
                self.makedirs(os.path.dirname(filename))
                with open(filename, "w") as stream:
                    output = template[platform].render(variables)
                    print(output, file=stream)

        # copy over configuration files
        configs = {}
        configs['nginx'] = [ 'nginx.conf', 'fastcgi_params' ]
        configs['apache'] = [ 'apache2.conf']

        # TODO: load global configuration variables from storage
        variables = {}

        for platform in platforms:
            for configfile in configs[platform]:
                templ = templateEnv.get_template(os.path.join(platform, configfile + ".j2"))
                filename = os.path.join(basedir, platform, configfile)
                self.makedirs(os.path.dirname(filename))
                with open(filename, "w") as stream:
                    output = templ.render(variables)
                    print(output, file=stream)



@register
class BindGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "bind")

        self.makedirs(basedir)
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


@register
class KnotGenerate(Generate):
    def generate(self):
        basedir = os.path.join(self.rootdir, "knot")
        templateLoader = jinja2.FileSystemLoader(searchpath="templates/")
        templateEnv = jinja2.Environment(loader=templateLoader, lstrip_blocks=False, trim_blocks=False)

        template = templateEnv.get_template('knot/knot.conf.j2')
        variables = {}
        variables['domains'] = self.db["domains"]
        filename = os.path.join(basedir, "knot.conf")
        self.makedirs(os.path.dirname(filename))
        with open(filename, "w") as stream:
            output = template.render(variables)
            print(output, file=stream)


def generate_all(db, rootdir):
    for cls in registered_classes:
        cls(db, rootdir).generate()
