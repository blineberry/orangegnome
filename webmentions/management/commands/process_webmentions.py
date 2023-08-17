from webmentions.models import OutgoingWebmention, OutgoingContent, IncomingWebmention

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        unprocessed_content = OutgoingContent.objects.filter(tries__lt=3)

        print(str(len(unprocessed_content)) + " unprocessed contents.")

        for content in unprocessed_content:
            content.process()

        unprocessed__outgoing_webmentions = OutgoingWebmention.objects.filter(success=False).filter(tries__lt=3)

        print(str(len(unprocessed__outgoing_webmentions)) + " unprocessed outgoing webmentions.")

        for mention in unprocessed__outgoing_webmentions:
            mention.try_notify_receiver()

        unprocessed_incoming_webmentions = IncomingWebmention.objects.filter(object_id=None).filter(tries__lt=3)

        print(str(len(unprocessed_incoming_webmentions)) + " unprocessed incoming webmentions.")

        for mention in unprocessed_incoming_webmentions:
            mention.process_and_save()