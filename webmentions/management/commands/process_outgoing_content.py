from webmentions.models import OutgoingContent

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        unprocessed_content = OutgoingContent.objects.filter(tries_lt=3)

        for content in unprocessed_content:
            content.process()