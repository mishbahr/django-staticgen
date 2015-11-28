#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, override_settings

from staticgen.exceptions import StaticgenError
from staticgen.staticgen_pool import StaticgenPool

from example.staticgen_views import ExampleStaticView


class TestStaticgenPool(TestCase):

    def setUp(self):
        self.staticgen_pool = StaticgenPool()

    @override_settings(STATICGEN_FAIL_SILENTLY=False)
    def test_register(self):
        self.staticgen_pool.register(ExampleStaticView)
        self.assertTrue('example.staticgen_views.ExampleStaticView' in self.staticgen_pool.modules)
        self.assertRaises(StaticgenError, self.staticgen_pool.register, ExampleStaticView)

    @override_settings(STATICGEN_FAIL_SILENTLY=False)
    def test_register_type(self):
        self.assertRaises(StaticgenError, self.staticgen_pool.register, object)
