#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, override_settings

from mock import patch

from staticgen.exceptions import StaticgenError
from staticgen.staticgen_views import StaticgenView

from example.staticgen_views import (
    ExampleDetailView,
    ExampleListView,
    ExampleStaticView
)


class TestStaticgenViews(TestCase):

    def test_base_staticgen_view_items(self):
        # base StaticgenView() - this should return empty list.
        staticgen_view = StaticgenView()
        self.assertEqual(len(staticgen_view.items()), 0)

    @patch('staticgen.staticgen_views.logger')
    def test_base_staticgen_log_error_logging(self, logger):
        staticgen_view = StaticgenView()
        message = 'Something bad happened'
        staticgen_view.log_error(message)
        self.assertTrue(logger.error.called)

    @override_settings(STATICGEN_FAIL_SILENTLY=False)
    def test_base_staticgen_log_error_exception(self):
        staticgen_view = StaticgenView()
        message = 'Something bad happened'
        self.assertRaises(StaticgenError, staticgen_view.log_error, message)

    def test_static_views(self):
        # should return 3 urls - homepage/error/redirect/sitemaps page: see example app urls
        module = ExampleStaticView()
        self.assertEqual(len(module.get_urls()), 4)

    def test_list_views(self):
        # should return 3 urls for Post ListView
        # first page without page number + 2 paginated page
        module = ExampleListView()
        self.assertEqual(len(module.get_urls()), 3)

    def test_detail_views(self):
        # should return 9 urls for Post DetailViews
        module = ExampleDetailView()
        self.assertEqual(len(module.get_urls()), 9)
