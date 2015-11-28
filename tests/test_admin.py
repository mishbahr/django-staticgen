#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import force_text
from mock import patch

from staticgen.models import LogEntry, Page


class TestStaticgenPageAdmin(TestCase):

    def setUp(self):
        for id in range(1, 6):
            path = '/page{0}/'.format(id)
            page = Page.objects.create(
                pk=id,
                path=path, site_id=settings.SITE_ID,
                publisher_state=Page.PUBLISHER_STATE_PUBLISHED)
            change_message = 'Added page {page}'.format(page=force_text(page))
            LogEntry.objects.log_action(change_message, page_id=id)

        LogEntry.objects.log_action('Change message', site_id=settings.SITE_ID)
        User.objects.create_superuser('super', 'super@example.com', 'secret')
        self.client.login(username='super', password='secret')

        self.publisher_url = reverse('admin:staticgen_page_publisher')
        self.page_changelist = reverse('admin:staticgen_page_changelist')

    def test_make_dirty_action(self):
        data = {
            'action': 'make_dirty',
            '_selected_action': Page.objects.all().values_list('pk', flat=True)
        }
        self.client.post(reverse('admin:staticgen_page_changelist'), data)
        self.assertEqual(Page.objects.changed().count(), 5)

    def test_history_view(self):
        response = self.client.get(reverse('admin:staticgen_page_history', args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['action_list']), 1)

    def test_publish_history_view(self):
        response = self.client.get(reverse('admin:staticgen_page_publish_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['action_list']), 1)

    @patch('staticgen.tasks.publish_pages.delay')
    def test_publish_view(self, mocked_task):
        # task to publish/update all registered pages should be called
        publish_url = '{url}?action=all'.format(url=self.publisher_url)
        response = self.client.get(publish_url)
        self.assertRedirects(response, self.page_changelist)
        self.assertTrue(mocked_task.called)

    @patch('staticgen.tasks.publish_pending.delay')
    def test_publish_pending_view(self, mocked_task):
        # task to publish pending pages should be called
        publish_url = '{url}?action=pending'.format(url=self.publisher_url)
        response = self.client.get(publish_url)

        self.assertRedirects(response, self.page_changelist)
        self.assertTrue(mocked_task.called)

    @patch('staticgen.tasks.publish_changed.delay')
    def test_publish_pending_view(self, mocked_task):
        # task to publish all pages marked as changed should be called
        publish_url = '{url}?action=changed'.format(url=self.publisher_url)
        response = self.client.get(publish_url)

        self.assertRedirects(response, self.page_changelist)
        self.assertTrue(mocked_task.called)

    @patch('staticgen.tasks.sync_pages.delay')
    def test_publish_pending_view(self, mocked_task):
        # task to sync all registered pages to db should be called
        publish_url = '{url}?action=sync'.format(url=self.publisher_url)
        response = self.client.get(publish_url)

        self.assertRedirects(response, self.page_changelist)
        self.assertTrue(mocked_task.called)

    def tearDown(self):
        self.client.logout()
