# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('esseff/esseff.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "cmdline-esseff",
    packages = ["esseff"],
    entry_points = {
        "console_scripts": ['esseff = esseff.esseff:main']
        },
    version = version,
    description = "Python command line application for deploying and versioning AWS Step Function state machines.",
    long_description = long_descr,
    author = "James Liljenquist",
    author_email = "jliljenq@gmail.com",
    url = "https://github.com/jimhub/esseff",
    )
