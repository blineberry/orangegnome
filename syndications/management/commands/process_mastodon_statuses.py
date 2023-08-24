from syndications.models import MastodonStatusesToProcess
from django.utils import timezone
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        statuses = MastodonStatusesToProcess.objects.all()

        print(str(len(statuses)) + " statuses to process.")

        for status in statuses:
            status.process()

        print(str(len(statuses)) + " statuses processed.")

    