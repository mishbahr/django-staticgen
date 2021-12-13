#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import staticgen

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = staticgen.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print('Tagging the version on github:')
    os.system('git tag -a %s -m "version %s"' % (version, version))
    os.system('git push --tags')
    sys.exit()

long_description = open('README.rst').read()

setup(
    name='django-staticgen',
    version=version,
    description="""Push your django powered site to Amazon S3.""",
    long_description=long_description,
    author='Mishbah Razzaque',
    author_email='mishbahx@gmail.com',
    url='https://github.com/mishbahr/django-staticgen',
    packages=[
        'staticgen',
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.7',
        'django-appconf',
        'django-storages-redux>=1.3',
        'six>=1.5.2',
        'boto>=2.28',
        'celery>=3.1',
        'beautifulsoup4>=4.4.0',
        'lxml==4.6.5',
    ],
    license='BSD',
    zip_safe=False,
    keywords='django-staticgen',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

    ],
)
