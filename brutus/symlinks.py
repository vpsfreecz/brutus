import os
import argparse
import yaml

from .utils import makedirs, symlink

def make_symlinks(target_dir, source_dir=os.path.realpath("./output")):
    with open("defaults/backends.yaml") as stream:
        config = yaml.load(stream)

    makedirs(target_dir)
    with open(os.path.join(target_dir, ".keep"), "w"):
        pass
    for service in config.values():
        for name, backend in service.items():
            for links in backend.get("links", []):
                source = os.path.join(source_dir, name, links["source"])
                target = os.path.join(os.path.realpath(target_dir), links["target"].lstrip("/"))
                makedirs(os.path.dirname(target))
                symlink(source, target)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help="Target directory")
    options = parser.parse_args()

    make_symlinks(options.target)

