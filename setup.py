#!/usr/bin/env python
from setuptools import setup, find_packages
try:
    import tinfoilhat
    version = tinfoilhat.__version__
    doc = tinfoilhat.__doc__
    author = tinfoilhat.__author__
except ImportError:
    # This will usually happen the first time setup.py is run in a new
    # virtualenv
    version = doc = author = ''


setup(
    name = 'TinfoilHat',
    version = version,
    description = doc.split('.')[0],
    long_description = open('README').read(),
    author=", ".join(author),
    url='http://github.com/pneff/tinfoilhat/tree/master',
    download_url='http://pypi.python.org/pypi/TinfoilHat',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        # Will require the version > 0.6.0 as soon as it's released
        'httplib2',
    ],
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
