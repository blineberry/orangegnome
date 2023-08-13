from webmentions.models import PendingIncomingWebmention,OutgoingWebmention

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        unprocessed_webmentions = PendingIncomingWebmention.objects.all()

        for mention in unprocessed_webmentions:
            mention.process_and_save()