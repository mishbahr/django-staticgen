#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from boto import connect_s3
from mock import patch, MagicMock
from moto import mock_s3

from staticgen.models import LogEntry, Page
from staticgen.publisher import StaticgenPublisher


class TestStaticgenPublisher(TestCase):
    """
    Expected pages list:

        '/',
        '/error.html',
        '/redirect/',
        '/sitemap.xml'

        '/posts/',
        '/posts/page/1/',
        '/posts/page/2/',

        '/posts/1/',
        '/posts/2/',
        '/posts/3/',
        '/posts/4/',
        '/posts/5/',
        '/posts/6/',
        '/posts/7/',
        '/posts/8/',
        '/posts/9/',

    Total = 16

    """

    def setUp(self):
        self.page1 = Page.objects.create(path='/page1/', site_id=settings.SITE_ID)
        self.page2 = Page.objects.create(path='/page2/', site_id=settings.SITE_ID)
        self.page3 = Page.objects.create(path='/page3/', site_id=settings.SITE_ID)

        self.publisher = StaticgenPublisher()

    def test_get_client(self):
        publisher_client = self.publisher.get_client()
        self.assertIsInstance(publisher_client, Client)

    @mock_s3
    def test_custom_header(self):
        response = self.publisher.get_page('/')
        self.assertTrue('HTTP_X_STATICGEN_PUBLISHER' in response.request.keys())

    def test_get_output_path(self):
        # add index.html if path ends with slash
        self.assertEqual(self.publisher.get_output_path('/'), 'index.html')
        # strip leftmost slash
        self.assertEqual(self.publisher.get_output_path('/sitemap.xml'), 'sitemap.xml')
        # return same string if not matching above rules
        self.assertEqual(self.publisher.get_output_path('errors/404.html'), 'errors/404.html')

    def test_get_queryset(self):
        # should return 3 pages we created during setup
        queryset = self.publisher.get_queryset()
        self.assertEqual(queryset.count(), 3)

    @patch('staticgen.publisher.logger')
    def test_log_error(self, publisher_logger):
        self.publisher.log_error(self.page1, 'Something went wrong.')
        self.assertEqual(LogEntry.objects.filter(page=self.page1).count(), 1)
        self.assertTrue(publisher_logger.error.called)

    @patch('staticgen.publisher.logger')
    def test_log_success(self, publisher_logger):
        self.publisher.log_success(self.page1, 'Something changed successfully.')
        self.assertEqual(LogEntry.objects.filter(page=self.page1).count(), 1)
        self.assertTrue(publisher_logger.info.called)

    @mock_s3
    def test_publish(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        # this will sync and publish all registered pages
        self.publisher.publish(sync=True)
        # all 16 pages should be published
        self.assertEqual(Page.objects.published().count(), 16)
        # there should be nothing pending after calling publish()
        self.assertEqual(Page.objects.pending().count(), 0)

        # check that page was successfully uploaded to S3 bucket
        for page in Page.objects.published():
            output_path = self.publisher.get_output_path(page.path)
            # bucket.get_key() returns None if key is not in the bucket
            self.assertIsNot(bucket.get_key(output_path), None)

    @mock_s3
    def test_handle_page_redirect(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        page = Page.objects.create(path=reverse('redirect_home'), site_id=settings.SITE_ID)
        client = self.publisher.get_client()

        output_path = self.publisher.get_output_path(page.path)
        response = client.get(page.path)

        key = bucket.new_key(output_path)
        page, has_changed = self.publisher.handle_page_redirect(page, response, key)
        self.assertTrue(has_changed)

        # test redirect location configured for S3 bucket
        # key.get_redirection() returns None using mock_s3! @todo
        # self.assertEqual(reverse('homepage'), key.get_redirect())

    @mock_s3
    def test_handle_page_upload(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        page = Page.objects.create(path=reverse('homepage'), site_id=settings.SITE_ID)
        client = self.publisher.get_client()

        output_path = self.publisher.get_output_path(page.path)
        response = client.get(page.path)

        key = bucket.new_key(output_path)
        page, has_changed = self.publisher.handle_page_upload(page, response, key)

        # for a new page i.e. unpublished pages, has_changed should be True
        self.assertTrue(has_changed)
        # check the page was uploaded successfully
        self.assertIsNot(bucket.get_key(output_path), None)

    @mock_s3
    def test_upload_to_s3_page_upload(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        page = Page.objects.create(path=reverse('homepage'), site_id=settings.SITE_ID)
        self.publisher.handle_page_upload = MagicMock(return_value=(page, True))

        self.publisher.publish()
        # publish should use handle_page_upload to process the page
        self.assertTrue(self.publisher.handle_page_upload.called)

    @mock_s3
    def test_upload_to_s3_page_redirect(self):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        redirected_page = Page.objects.create(
            path=reverse('redirect_home'), site_id=settings.SITE_ID)
        self.publisher.handle_page_redirect = MagicMock(return_value=(redirected_page, True))

        self.publisher.publish()
        # publish should use handle_page_redirect to process the page
        self.assertTrue(self.publisher.handle_page_redirect.called)

    @mock_s3
    @patch('staticgen.publisher.logger')
    def test_publish_deletion(self, publisher_logger):
        # setUp
        connection = connect_s3()
        connection.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket = connection.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        # upload some content to S3 bucket
        uploaded_keys = []
        for page in (self.page1, self.page2, self.page3):
            output_path = self.publisher.get_output_path(page.path)

            key = bucket.get_key(output_path) or bucket.new_key(output_path)
            content = 'This is page {id} - path: {path}'.format(id=page.pk, path=page.path)
            key.set_contents_from_string(content)
            key.make_public()

            uploaded_keys.append(key.name)

        # Sync will mark page1/page2/page3 as deleted.
        Page.objects.sync()

        # actual test - publish_deletion should delete page1/page2/page3
        # from the bucket and the database
        self.publisher.publish_deletion()

        # test database record for page has been deleted.
        self.assertEqual(Page.objects.deleted().count(), 0)
        # test the deletion was logged.
        self.assertTrue(publisher_logger.info.called)

        # test the pages was removed successfully from the bucket
        remote_keys = [s3_key.name for s3_key in bucket.list()]
        for key in uploaded_keys:
            self.assertNotIn(key, remote_keys)
