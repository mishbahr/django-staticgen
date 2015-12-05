# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from mock import Mock

from staticgen.context_processors import staticgen_publisher


class TestStaticgenContextProcessors(TestCase):

    def test_request_with_custom_header(self):
        request = Mock()
        request.META = {'HTTP_X_STATICGEN_PUBLISHER': True}

        context = staticgen_publisher(request)

        self.assertTrue('STATICGEN_IS_PUBLISHING' in context.keys())
        self.assertTrue(context['STATICGEN_IS_PUBLISHING'])

        self.assertTrue('STATICGEN_BASE_URL' in context.keys())
        self.assertTrue(context['STATICGEN_BASE_URL'], settings.STATICGEN_STATIC_SITE_DOMAIN)
