#!/usr/bin/python

from __future__ import print_function, unicode_literals

# Python 2.x tweak
from io import open

import os
import jinja2
import yaml
import base64
import subprocess
import tempfile

from . import utils

registered_classes = []


def register(cls):
    registered_classes.append(cls)
    return cls


class Generate:
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="templates"), trim_blocks=True)

    def __init__(self, db, rootdir, generate_keys):
        self.db = db
        self.rootdir = rootdir
        self.generate_keys = generate_keys

    def generate_file(self, name, **kargs):
        template = "{}/{}.j2".format(self.name, name)
        target = os.path.join(self.rootdir, self.name, name)

        output = self.template_env.get_template(template).render(**kargs)
        # jinja2 seems to sometimes drop the final newline before end of file.
        if not output.endswith("\n"):
            output += "\n"

        utils.makedirs(os.path.dirname(target))
        print(target)
        with open(target, "w") as stream:
            stream.write(output)


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

        # for LE
        for domain in self.db['domains']:
            if 'tsigid' not in self.db["domains"][domain]:
                self.db["domains"][domain]["tsigid"] = domain + ".LE.KEY"
                self.db["domains"][domain]["aclid"] = domain + ".LE.ACL"
                randomtext = os.urandom(int(int(256)/8))
                tsigsecret = base64.b64encode(randomtext).decode("utf-8")
                self.db["domains"][domain]["tsigsecret"] = tsigsecret if self.generate_keys else ""

        variables = {}
        variables['domains'] = self.db["domains"]

        filename = os.path.join(basedir, "knot.conf")
        utils.makedirs(os.path.dirname(filename))
        with open(filename, "w") as stream:
            output = template.render(variables)
            print(output, file=stream)


@register
class LetsencryptGenerate(Generate):
    service = "certificates"
    name = "letsencrypt"

    def create_RSA_key(self):
        return subprocess.check_output(["openssl", "genrsa", "4096"])

    def create_CSR(self, san, key):
        with open("/etc/ssl/openssl.cnf") as sslconf:
            openssl_csr_config = sslconf.read()
        san_config = "[SAN]\nsubjectAltName=" + ",".join(["DNS:" + domain for domain in san])
        openssl_csr_config = openssl_csr_config + san_config

        tempdir = tempfile.mkdtemp()
        keyfifo = os.path.join(tempdir, 'keyfifo')
        conffifo = os.path.join(tempdir, 'conffifo')
        keyfd = os.open(keyfifo, os.O_WRONLY|os.O_CREAT)
        os.write(keyfd, key)
        os.close(keyfd)
        with open(conffifo, 'w') as pipe:
            pipe.write(openssl_csr_config)
        ossl = subprocess.Popen(['openssl', 'req', '-new', '-sha256', '-key', keyfifo, '-subj', '/', '-reqexts', 'SAN', '-config', conffifo], stdout=subprocess.PIPE)
        out, err = ossl.communicate()
        return out

    def generate(self):
        if self.generate_keys and 'letsencrypt_account_key' not in self.db["instances"][None]:
            self.db["instances"][None]["letsencrypt_account_key"] = self.create_RSA_key()

        basedir = os.path.join(self.rootdir, self.name, "etc", "letsencrypt")
        template = self.template_env.get_template('letsencrypt/le.ini.j2')
        for name, value in sorted(self.db["domains"].items()):
            if ('dns' not in value['services']) or ('tsigsecret' not in value):
                continue
            variables = {
                'domain': name,
                'tsigid': value['tsigid'],
                'tsigsecret': value['tsigsecret'] if self.generate_keys else "",
                'admin_mail': self.db["instances"][None].get("admin_mail", ""),
                'acme_dir': 'https://acme-staging.api.letsencrypt.org/directory',
                'dns': 'localhost',
            }
            if self.generate_keys and 'letsencrypt_domain_key' not in value:
                self.db["domains"][name]["letsencrypt_domain_key"] = self.create_RSA_key()
                san = [domain for domain in self.db["websites"]]
                csr = self.create_CSR(san, self.db["domains"][name]["letsencrypt_domain_key"])
                utils.makedirs(basedir)
                keyfd = os.open(os.path.join(basedir, name + '.csr'), os.O_WRONLY | os.O_CREAT)
                os.write(keyfd, csr)
                os.close(keyfd)

            filename = os.path.join(basedir, name + ".ini")
            utils.makedirs(os.path.dirname(filename))
            with open(filename, "w") as stream:
                output = template.render(variables)
                print(output, file=stream)


def generate_all(db, rootdir, generate_keys=True):
    for cls in registered_classes:
        services = db["instances"][None]["services"]
        # Skip disabled services
        if not services.get(cls.service):
            continue
        cls(db, rootdir, generate_keys).generate()
