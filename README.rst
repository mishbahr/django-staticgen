================
django-staticgen
================

.. image:: http://img.shields.io/travis/mishbahr/django-staticgen.svg?style=flat-square
    :target: https://travis-ci.org/mishbahr/django-staticgen/

.. image:: http://img.shields.io/pypi/v/django-staticgen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-staticgen/
    :alt: Latest Version

.. image:: http://img.shields.io/pypi/dm/django-staticgen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-staticgen/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/pyversions/django-staticgen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-staticgen/
    :alt: Python Versions

.. image:: http://img.shields.io/pypi/l/django-staticgen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-staticgen/
    :alt: License

.. image:: http://img.shields.io/coveralls/mishbahr/django-staticgen.svg?style=flat-square
  :target: https://coveralls.io/r/mishbahr/django-staticgen?branch=master

Push your django powered site to Amazon S3.

**WORK IN PROGRESS // NOT PRODUCTION READY.**

Demo
----

Live Site: http://staticgen-demo.herokuapp.com

Static Site: http://staticgen-demo.s3-website-us-west-2.amazonaws.com

Source code for demo: http://github.com/mishbahr/staticgen-demo

Quickstart
----------

1. Install ``django-staticgen`` from PyPi::

    pip install django-staticgen

2. Add ``staticgen`` to ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'staticgen',
        ...
    )

3. Migrate database::

    python manage.py migrate

4. To publish your site on Amazon S3, you'll need to setup an AWS S3 bucket to host the website. Add the following details to your projects ``settings.py`` module::

    AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
    AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    AWS_STORAGE_BUCKET_NAME = 'staticgen-bucket'

5. Finally, publishing your site to S3 is as simple as::

     python manage.py staticgen_publish


Celery
-------

This project requires ``celery>=3.1`` to be properly installed and configured.

For more information on using Celery with Django.

See: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html


Todo
----

* Cache Control
* Gzip Compression
* CloudFront distribution/invalidation