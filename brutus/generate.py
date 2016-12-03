#!/usr/bin/python

from __future__ import print_function, unicode_literals

# Python 2.x tweak
from io import open

import os
import jinja2
import yaml

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


class WebserverGenerate(Generate):
    service = "webserver"

    def load_defaults(self):
        with open('defaults/webserver.yaml') as stream:
            return yaml.safe_load(stream)

    def generate(self, site_template, output_dir, conf_files, conf_dir):
        basedir = os.path.join(self.rootdir)

        template = self.template_env.get_template(site_template)
        for item in self.db["websites"].values():
            variables = self.load_defaults()
            variables.update(item)

            # set defaults
            variables['id'] = variables['domain'] if variables['id'] is None else variables['id']
            variables['name'] = variables['id'] if variables['name'] is None else variables['name']
            variables['root'] = "/srv/www/" + variables['domain'] + "/" + variables['id'] + "/www" \
                if variables['root'] is None else variables['root']

            filename = os.path.join(basedir, self.name, output_dir,  item['id'] + ".conf")
            utils.makedirs(os.path.dirname(filename))
            with open(filename, "w") as stream:
                output = template.render(variables)
                print(output, file=stream)

            for configfile in conf_files:
                templ = self.template_env.get_template(os.path.join(self.name, configfile + ".j2"))
                filename = os.path.join(basedir, self.name, conf_dir, configfile)
                utils.makedirs(os.path.dirname(filename))
                with open(filename, "w") as stream:
                    output = templ.render(variables)
                    print(output, file=stream)


@register
class NginxGenerate(WebserverGenerate):
    name = "nginx"

    def generate(self):
        site_template = "nginx/site.conf.j2"
        output_dir = "etc/nginx/conf.d"
        conf_files = ["nginx.conf", "fastcgi_params"]
        conf_dir = "etc/nginx"

        return WebserverGenerate.generate(self, site_template, output_dir, conf_files, conf_dir)


@register
class ApacheGenerate(WebserverGenerate):
    name = "apache"

    def generate(self):
        site_template = "apache/site.conf.j2"
        output_dir = "etc/apache/conf.d"
        conf_files = ["apache2.conf"]
        conf_dir = "etc/apache"

        return WebserverGenerate.generate(self, site_template, output_dir, conf_files, conf_dir)


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
