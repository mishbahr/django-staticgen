# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import DetailView, ListView, TemplateView, RedirectView
from .models import Post


class IndexView(TemplateView):
    template_name = 'example/home.html'


class ErrorView(TemplateView):
    template_name = 'example/error.html'


class PostListView(ListView):
    model = Post
    paginate_by = 5
    context_object_name = 'post_list'
    template_name = 'example/post_list.html'


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'example/post_detail.html'


class RedirectToHomeView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'homepage'
