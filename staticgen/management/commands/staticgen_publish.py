# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from staticgen.publisher import StaticgenPublisher


class Command(BaseCommand):

    help = 'Publish/update all registered pages to Amazon S3.'

    def handle(self, *args, **options):
        start_time = time.time()

        publisher = StaticgenPublisher()
        publisher.publish(sync=True)

        verbosity = int(options.get('verbosity'))
        if verbosity >= 1:
            elapsed_time = time.time() - start_time
            message = _('Completed publishing request successfully, '
                        'in {elapsed_time:.2f} seconds.').format(elapsed_time=elapsed_time)
            self.stdout.write(message)
