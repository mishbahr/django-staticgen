# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from example.sitemaps import ExampleSitemap
from staticgen.helpers import get_static_site_domain
from staticgen.sitemaps import override_sitemaps_domain


class TestStaticgenSitemapsDomainOverride(TestCase):

    def test_domain_override(self):
        sitemaps = override_sitemaps_domain({'test': ExampleSitemap})
        sitemap = sitemaps['test']
        if callable(sitemap):
            sitemap = sitemap()

        url = sitemap.get_urls()[0]
        domain = 'http://{domain}'.format(domain=get_static_site_domain())
        self.assertTrue(url['location'].startswith(domain))
