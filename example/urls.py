# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from staticgen.sitemaps import override_sitemaps_domain

from .views import ErrorView, IndexView, PostDetailView, PostListView, RedirectToHomeView
from .sitemaps import ExampleSitemap

admin.autodiscover()


sitemaps = {
    'posts': ExampleSitemap
}

urlpatterns = patterns(
    '',
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': override_sitemaps_domain(sitemaps)},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', IndexView.as_view(), name='homepage'),
    url(r'^error\.html$', ErrorView.as_view(), name='error_page'),
    url(r'^redirect/$', RedirectToHomeView.as_view(), name='redirect_home'),
    url(r'^posts/$', PostListView.as_view(), name='post_list'),
    url(r'^posts/page/(?P<page>\d+)/$', PostListView.as_view(), name='post_list'),
    url(r'^posts/(?P<pk>[-\w]+)/$', PostDetailView.as_view(), name='post_detail'),
)
