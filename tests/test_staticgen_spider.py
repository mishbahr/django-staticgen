# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase, override_settings

from staticgen.exceptions import StaticgenError
from staticgen.staticgen_spider import StaticgenSpider


class TestStaticgenSpider(TestCase):

    def setUp(self):
        self.spider = StaticgenSpider()

    @override_settings(STATICGEN_SITEMAP_URL='sitemap.xml')
    def test_get_sitemap_url_from_settings(self):
        sitemap_url = self.spider.get_sitemap_url()
        self.assertEqual(sitemap_url, 'sitemap.xml')

    def test_get_sitemap_url_autodiscover(self):
        sitemap_url = self.spider.get_sitemap_url()
        self.assertEqual(sitemap_url, '/sitemap.xml')

    @override_settings(ROOT_URLCONF=(), STATICGEN_FAIL_SILENTLY=False)
    def test_get_sitemap_url_raises_error(self):
        self.assertRaises(StaticgenError, self.spider.get_sitemap_url)

    def test_get_sitemap_links(self):
        links = self.spider.get_sitemap_links()
        # should be 9 urls - for 9 posts urls in sitemap
        self.assertEqual(len(links), 9)

    def test_clean_urls_with_bad_urls(self):
        bad_urls = (
            '{media_url}user-upload.jpg'.format(media_url=settings.MEDIA_URL),
            '{static_url}logo.jpg'.format(static_url=settings.STATIC_URL),
            '#page-top',
            'mailto:staticgen@example.com',
            'http://twitter.com/staticgen/'
        )

        for url in bad_urls:
            self.assertEqual(self.spider.clean_url(url), None)

    def test_clean_urls_with_good_url(self):
        good_urls = (
            ('/staticgen/', '/staticgen/'),
            ('http://example.com/staticgen/', '//example.com/staticgen/'),
            ('https://example.com/staticgen/', '//example.com/staticgen/'),
            ('http://www.example.com/staticgen/', '//example.com/staticgen/'),
            ('https://www.example.com/staticgen/', '//example.com/staticgen/'),
        )

        for url, cleaned_url in good_urls:
            self.assertEqual(self.spider.clean_url(url), cleaned_url)

    def test_get_pages(self):
        # should be 9 posts detailview + 1 post listview + homepage + 1 redirect view = 12 pages
        urls = self.spider.get_urls()
        self.assertEqual(len(urls), 12)
