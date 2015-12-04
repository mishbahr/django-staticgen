# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.test import Client

from bs4 import BeautifulSoup

from .conf import settings
from .exceptions import StaticgenError
from .status import is_redirect, is_success


try:
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover
    # Python 2.X
    from urlparse import urlparse


logger = logging.getLogger('staticgen')


class UrlRegistry(object):

    def __init__(self):
        self.visited = set()
        self.to_visit = set()

    def enqueue(self, url):
        if url and url not in self.visited:
            self.to_visit.add(url)

    def __iter__(self):
        while self.to_visit:
            url = self.to_visit.pop()
            self.visited.add(url)
            yield url


class StaticgenCrawler(object):

    def __init__(self):
        current_site = Site.objects.get_current()
        self.base_domain = current_site.domain
        self.url_registry = UrlRegistry()
        self.client = Client()

    def log_error(self, message):
        logger.error(message)
        if not settings.STATICGEN_FAIL_SILENTLY:
            raise StaticgenError(message)

    def clean_url(self, url):
        url = url.lower().strip()

        special_links = [
            url.startswith(prefix) for prefix in ('mailto', 'tel', 'sms', 'skype', 'geo')]

        if any([url.startswith(settings.MEDIA_URL),  # skip media files urls
                url.startswith(settings.STATIC_URL),  # skip static files urls
                url.startswith('#')] + special_links):  # skip anchors & special links e.g 'tel:'
            return None

        if url.startswith('/'):
            return url

        # strip web prefixes
        for prefix in ('http://', 'https://', 'www.', ):
            if url.startswith(prefix):
                url = url[len(prefix):]

        if not url.startswith(self.base_domain):
            return None

        return '//{url}'.format(url=url)

    def get_sitemap_url(self):
        sitemap_url = settings.STATICGEN_SITEMAP_URL
        if sitemap_url is None:
            try:
                # Try for the "global" sitemap URL.
                sitemap_url = reverse('django.contrib.sitemaps.views.sitemap')
            except NoReverseMatch:
                message = _('You did not provide a sitemap_url, '
                            'and the sitemap URL could not be auto-detected.')
                self.log_error(message)

        return sitemap_url

    def get_sitemap_links(self):
        urls = []
        sitemap_url = self.get_sitemap_url()
        if sitemap_url:
            response = self.client.get(sitemap_url)
            if not is_success(response.status_code):  # pragma: no cover
                message = _('Error retrieving sitemap: {sitemap_url} - Code: {code}').format(
                    sitemap_url=sitemap_url, code=response.status_code)
                self.log_error(message)
            else:
                soup = BeautifulSoup(response.content, 'lxml')
                urls = [loc.get_text() for loc in soup.find_all('loc')]

        return urls

    @staticmethod
    def get_links(response):
        links = []

        if is_redirect(response.status_code):
            links.append(response['Location'])

        if is_success(response.status_code):
            soup = BeautifulSoup(response.content,  'lxml')
            for link in soup.find_all('a', href=True):
                links.append(link['href'])

        return links

    def get_urls(self):
        urls = []

        sitemap_links = self.get_sitemap_links()
        for url in sitemap_links:
            parsed_url = urlparse(url)
            self.url_registry.enqueue(parsed_url.path)

        for url in self.url_registry:
            urls.append(url)

            response = self.client.get(url)
            for link in self.get_links(response):
                cleaned_url = self.clean_url(link)
                if cleaned_url:
                    parsed_url = urlparse(cleaned_url)
                    self.url_registry.enqueue(parsed_url.path)

        urls = list(set(urls))
        urls.sort()
        return urls
