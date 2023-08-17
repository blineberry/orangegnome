from webmentions.models import IncomingWebmention

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        unprocessed_webmentions = IncomingWebmention.objects.filter(content_object=None).filter(tries_lt=3)

        for mention in unprocessed_webmentions:
            mention.process_and_save()