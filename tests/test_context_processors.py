# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from mock import Mock

from staticgen.context_processors import staticgen_publisher


class TestStaticgenContextProcessors(TestCase):

    def test_request_with_custom_header(self):
        request = Mock()
        request.META = {'HTTP_X_STATICGEN_PUBLISHER': True}

        context = staticgen_publisher(request)

        self.assertTrue('is_publishing' in context.keys())
        self.assertTrue(context['is_publishing'])
