# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import time

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from celery import shared_task

from .models import LogEntry, Page
from .publisher import StaticgenPublisher

logger = logging.getLogger('staticgen')


def log_action(message):
    message = force_text(message)
    logger.info(message)
    LogEntry.objects.log_action(message)


@shared_task()
def sync_pages():
    message = _('Received task to sync all registered pages.')
    log_action(message)

    start_time = time.time()

    Page.objects.sync()

    elapsed_time = time.time() - start_time
    message = _('Synced all registered pages successfully, '
                'in {elapsed_time:.2f} seconds.').format(elapsed_time=elapsed_time)
    log_action(message)


@shared_task
def publish_pending():
    message = _('Received task to publish all pending pages.')
    log_action(message)

    start_time = time.time()

    publisher = StaticgenPublisher()
    publisher.publish(pending=True)

    elapsed_time = time.time() - start_time
    message = _('Published all pending pages successfully, '
                'in {elapsed_time:.2f} seconds.').format(elapsed_time=elapsed_time)
    log_action(message)


@shared_task
def publish_changed():
    message = _('Received task to publish all pages marked as changed.')
    log_action(message)

    start_time = time.time()

    publisher = StaticgenPublisher()
    publisher.publish(changed=True)

    elapsed_time = time.time() - start_time
    message = _('Published all pages marked as changed successfully, '
                'in {elapsed_time:.2f} seconds.').format(elapsed_time=elapsed_time)
    log_action(message)


@shared_task
def publish_pages():
    message = _('Received task to publish/update all registered pages.')
    logger.info(force_text(message))
    LogEntry.objects.log_action(message)

    start_time = time.time()

    publisher = StaticgenPublisher()
    publisher.publish(sync=True)

    elapsed_time = time.time() - start_time
    message = _('Published or updated all registered pages successfully, '
                'in {elapsed_time:.2f} seconds.').format(elapsed_time=elapsed_time)
    logger.info(message)
