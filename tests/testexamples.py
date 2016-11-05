#!/usr/bin/python

import os
import yaml

def test_examples():
    for filename in os.listdir("examples/"):
        with open(os.path.join("examples", filename)) as stream:
            print(yaml.load(stream))
