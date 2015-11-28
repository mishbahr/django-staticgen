# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase

from boto import connect_s3
from moto import mock_s3

from example.sitemaps import ExampleSitemap
from staticgen.sitemaps import override_sitemaps_domain


class TestStaticgenSitemapsDomainOverride(TestCase):

    @mock_s3
    def test_domain_override(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        # actual test
        sitemaps = override_sitemaps_domain({'test': ExampleSitemap})
        sitemap = sitemaps['test']
        if callable(sitemap):
            sitemap = sitemap()

        url = sitemap.get_urls()[0]
        domain = 'http://{domain}'.format(domain=bucket.get_website_endpoint())
        self.assertTrue(url['location'].startswith(domain))
