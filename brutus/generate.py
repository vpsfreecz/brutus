#!/usr/bin/python

import os
import jinja2

rootdir = "output"

class PostfixGenerate:
    def __init__(self, db):
        self.db = db
        self.basedir =  os.path.join(rootdir, "postfix")

    def generate(self):
        filename = os.path.join(self.basedir, "domains")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as stream:
            for item in self.db["domains"].values():
                print("{id} none".format(**item), file=stream)

class DovecotGenerate:
    def __init__(self, db):
        self.db = db
        self.basedir =  os.path.join(rootdir, "dovecot")

    def generate(self):
        filename = os.path.join(self.basedir, "passwd")

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as stream:
            for item in self.db["accounts"].values():
                if {"domain", "password"}.issubset(item.keys()):
                    print("{id}@{domain}:{{{password[scheme]}}}{password[data]}".format(**item), file=stream)

class NginxGenerate:
    def __init__(self, db):
        self.db = db
        self.basedir =  os.path.join(rootdir, "nginx")

    def generate(self):
        templateLoader = jinja2.FileSystemLoader(searchpath="templates/")
        templateEnv = jinja2.Environment(loader=templateLoader)
        nginx_site_template_name = "nginx/site.conf"
        template = templateEnv.get_template(nginx_site_template_name)

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

            filename = os.path.join(self.basedir, item['id'] + ".conf")
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as stream:
                output = template.render(variables)
                print(output, file=stream)

def generate_all(db):
    PostfixGenerate(db).generate()
    DovecotGenerate(db).generate()
    NginxGenerate(db).generate()
