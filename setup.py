#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import sys
from shutil import rmtree

from setuptools import find_namespace_packages, setup, Command

# Package meta-data.
ORG = 'redditnfl'
NAME = 'rnfltools'
DESCRIPTION = 'r/NFL tools'
URL = 'https://github.com/redditnfl/rnfl-tools'
EMAIL = 'rasher@rasher.dk'
AUTHOR = 'Jonas Häggqvist'

# What packages are required for this module to be executed?
REQUIRED = [
        'google-api-python-client>=1.7.4,<1.8',
        'oauth2client>=4.1.3,<4.2',
        'nfltools @ git+ssh://git@github.com/redditnfl/nfltools.git@e3b48de',
        'reddittools @ git+ssh://git@github.com/redditnfl/reddittools.git@8048abc',
        'nflapi @ git+ssh://git@github.com/rasher/nflapi.git@f411d5e',
        'Jinja2>=2.10.3,<2.11',
]
DEPENDENCY_LINKS = [
]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, ORG, NAME, '__version__.py')) as f:
    exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()

from pprint import pprint
pprint(find_namespace_packages(exclude=('tests*', 'build*', 'dist*',)))

# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_namespace_packages(exclude=('tests*', 'build*', 'dist*')),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    entry_points={
        'console_scripts': [
            #'nfl-schedule=redditnfl.nfltools.nflcom.schedule:main',
            'pingrules=redditnfl.rnfltools.pingrules:main',
            ],
    },
    install_requires=REQUIRED,
    dependency_links=DEPENDENCY_LINKS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
