# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf import settings
from django.test import TestCase, override_settings

from boto import connect_s3
from moto import mock_s3

from staticgen.helpers import get_static_site_domain


class TestStaticgenHelpers(TestCase):

    @mock_s3
    @override_settings(STATICGEN_STATIC_SITE_DOMAIN=None)
    def test_request_with_custom_header(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        static_domain = get_static_site_domain()
        self.assertEqual(static_domain, 'staticgen-bucket.s3-website-us-east-1.amazonaws.com')