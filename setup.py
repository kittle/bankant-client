#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "bankant-client",
    version = "0.0.1",
    description = "BankAnt API client library",
    author = "Andrey Gerzhov",
    author_email = "kittle@humgat.org",
    license = "BSD License",
    url = "https://github.com/kittle/bankant-client",
    packages = ["bankant_client"],
    # package_data = {"": ["templates/*"]},
    long_description = "",
    install_requires=[
       'requests==0.14.1',
       ]
)
