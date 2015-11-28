# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from staticgen.staticgen_pool import staticgen_pool
from staticgen.staticgen_views import StaticgenView

from .models import Post


class ExampleStaticView(StaticgenView):

    def items(self):
        return (
            'homepage',
            'error_page',
            'redirect_home',
            'sitemaps',
        )


class ExampleListView(StaticgenView):
    is_paginated = True

    def items(self):
        return ('post_list', )


class ExampleDetailView(StaticgenView):

    def items(self):
        return Post.objects.all()


staticgen_pool.register(ExampleStaticView)
staticgen_pool.register(ExampleListView)
staticgen_pool.register(ExampleDetailView)
