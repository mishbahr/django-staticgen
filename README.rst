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

.. image:: http://img.shields.io/pypi/l/django-staticgen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-staticgen/
    :alt: License

.. image:: http://img.shields.io/coveralls/mishbahr/django-staticgen.svg?style=flat-square
  :target: https://coveralls.io/r/mishbahr/django-staticgen?branch=master

Simple static site generator for django. Inspired by django-bakery.

**WORK IN PROGRESS // NOT PRODUCTION READY.**


Demo
----

Live Site: https://staticgen-demo.herokuapp.com

Static Site: http://staticgen-demo.s3-website-us-west-2.amazonaws.com

Admin: https://staticgen-demo.herokuapp.com/manage

Message me on Twitter `@mishbahrazzaque <https://twitter.com/mishbahrazzaque>`_ for login details.

Source code for demo: https://github.com/mishbahr/staticgen-demo


Quickstart
----------

1. Install ``django-staticgen``::

    pip install django-staticgen

2. Add ``staticgen`` to ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'staticgen',
        ...
    )

3. Migrate database::

    python manage.py migrate

4. ``django-staticgen`` requires celery>=3.1 to be installed and configured correctly. For more information on using Celery with Django::

    http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html