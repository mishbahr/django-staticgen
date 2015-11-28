# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap

from .models import Post


class ExampleSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Post.objects.all()
