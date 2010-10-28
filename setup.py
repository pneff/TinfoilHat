#!/usr/bin/env python
from setuptools import setup, find_packages
import paranoidlib
setup(
    name = 'paranoidlib',
    version = paranoidlib.__version__,
    description = paranoidlib.__doc__.split('.')[0],
    author=", ".join(paranoidlib.__author__),
    url='http://github.com/pneff/paranoidlib/tree/master',
    download_url='http://pypi.python.org/pypi/paranoidlib',
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
