#!/usr/bin/python

import shutil, subprocess
from nose.tools import assert_equal

from brutus.symlinks import make_symlinks

def test_symlinks():
    rootdir = "tmp/symlinks"

    shutil.rmtree(rootdir, ignore_errors=True)
    make_symlinks(rootdir, "BRUTUS_DIR")

    subprocess.check_call([
        "diff",
        "--recursive",
        "--no-dereference",
        rootdir,
        "tests/symlinks"])
    assert_equal(subprocess.check_output(
        "find tests/symlinks/ -not -type l -and -not -type d -and -not -name '.keep'",
        shell=True, universal_newlines=True), "")
