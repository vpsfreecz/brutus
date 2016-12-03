#!/usr/bin/python

from __future__ import print_function

import os
import jinja2

from . import utils

registered_classes = []

def register(cls):
    registered_classes.append(cls)
    return cls


class Generate:
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="templates"), trim_blocks=True)

    def __init__(self, db, rootdir):
        self.db = db
        self.rootdir = rootdir


@register
class PostfixGenerate(Generate):
    service = "mailserver"
    name = "postfix"

    def generate(self):
        basedir = os.path.join(self.rootdir, "postfix", "etc", "postfix")
        filename = os.path.join(basedir, "domains")

        utils.makedirs(os.path.dirname(filename))
        with open(filename, "w") as stream:
            for item in self.db["domains"].values():
                print("{id} none".format(**item), file=stream)


@register
class DovecotGenerate(Generate):
    service = "mailserver"
    name = "dovecot"

    def generate(self):
        basedir = os.path.join(self.rootdir, "dovecot", "etc", "dovecot")
        filename = os.path.join(basedir, "passwd")

        utils.makedirs(os.path.dirname(filename))
        with open(filename, "w") as stream:
            for item in self.db["accounts"].values():
                if {"domain", "password"}.issubset(item.keys()):
                    print("{id}@{domain}:{{{password[scheme]}}}{password[data]}".format(**item), file=stream)


@register
class WebserverGenerate(Generate):
    service = "webserver"
    name = "nginx_apache"

    def generate(self):
        basedir = os.path.join(self.rootdir)

        platforms = [ 'nginx', 'apache' ];
        template = {};

        for platform in platforms:
            template[platform] = self.template_env.get_template(platform + '/site.conf.j2')

        defaults = {
            "id": None,
            "name": None,
            "root": None,
            "tls": "letsencrypt",
            "tls_params": None,
            "php": "false",
            "headers": None,
            "locations": None,
            "http2": "true",
        }

        for item in self.db["websites"].values():
            variables = defaults.copy()
            variables.update(item)

            # set defaults
            variables['id'] = variables['domain'] if variables['id'] is None else variables['id']
            variables['name'] = variables['id'] if variables['name'] is None else variables['name']
            variables['root'] = "/srv/www/" + variables['domain'] + "/" + variables['id'] + "/www" if variables['root'] is None else variables['root']

            for platform in platforms:
                filename = os.path.join(basedir, platform, "etc", platform, 'conf.d',  item['id'] + ".conf")
                utils.makedirs(os.path.dirname(filename))
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
                templ = self.template_env.get_template(os.path.join(platform, configfile + ".j2"))
                filename = os.path.join(basedir, platform, "etc", platform, configfile)
                utils.makedirs(os.path.dirname(filename))
                with open(filename, "w") as stream:
                    output = templ.render(variables)
                    print(output, file=stream)



@register
class BindGenerate(Generate):
    service = "dnsserver"
    name = "bind"

    def generate(self):
        basedir = os.path.join(self.rootdir, "bind", "etc", "bind")

        utils.makedirs(basedir)
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
    service = "dnsserver"
    name = "knot"

    def generate(self):
        basedir = os.path.join(self.rootdir, "knot", "etc", "knot")
        templateLoader = jinja2.FileSystemLoader(searchpath="templates/")

        template = self.template_env.get_template('knot/knot.conf.j2')
        variables = {}
        variables['domains'] = self.db["domains"]
        filename = os.path.join(basedir, "knot.conf")
        utils.makedirs(os.path.dirname(filename))
        with open(filename, "w") as stream:
            output = template.render(variables)
            print(output, file=stream)


def generate_all(db, rootdir):
    for cls in registered_classes:
        services = db["instances"][None]["services"]
        # Skip disabled services
        if not services.get(cls.service):
            continue
        cls(db, rootdir).generate()
