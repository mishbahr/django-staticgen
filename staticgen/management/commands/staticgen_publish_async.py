# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from staticgen.tasks import publish_pages


class Command(BaseCommand):

    help = 'Publish/update all registered pages to Amazon S3 via a Celery task.'

    def handle(self, *args, **options):
        publish_pages.delay()

        verbosity = int(options.get('verbosity'))
        if verbosity >= 1:
            message = _('Your publishing request is processing in the background via Celery')
            self.stdout.write(message)
