#!/usr/bin/env python
from setuptools import setup, find_packages
import tinfoilhat
setup(
    name = 'TinfoilHat',
    version = tinfoilhat.__version__,
    description = tinfoilhat.__doc__.split('.')[0],
    author=", ".join(tinfoilhat.__author__),
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
