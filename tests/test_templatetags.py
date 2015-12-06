# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from staticgen.templatetags.staticgen_tags import routable_pageurl


class TestStaticgenRoutablePageTemplateTag(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.request = self.rf.get(reverse('post_list'))
        self.context = {'request': self.request}

    def test_routable_pageurl_templatetag(self):
        self.assertEqual(routable_pageurl(self.context, 2), '/posts/page/2/')
