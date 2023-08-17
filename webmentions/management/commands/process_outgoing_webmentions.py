from webmentions.models import OutgoingWebmention

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        unprocessed_webmentions = OutgoingWebmention.objects.filter(success=False).filter(tries_lt=3)

        for mention in unprocessed_webmentions:
            mention.try_notify_receiver()