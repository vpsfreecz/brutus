#!/usr/bin/python

from setuptools import setup, find_packages
import nose

setup(
    name="brutus",
    version="0.0.1",
    description="",
    author="Pavel Šimerda",
    author_email="pavlix@pavlix.net",
    scripts=["brutus-db", "brutus-generate"],
    packages=find_packages(),
    testssuite=nose.collector
)
