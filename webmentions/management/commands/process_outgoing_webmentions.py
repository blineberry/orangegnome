from webmentions.models import PendingOutgoingWebmention,OutgoingWebmention

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        unprocessed_webmentions = PendingOutgoingWebmention.objects.filter(processed=False)

        for mention in unprocessed_webmentions:
            content_mentions = mention.get_source_content_mentions_and_save()

            for content_mention in content_mentions:
                get_or_create = OutgoingWebmention.objects.get_or_create(source=mention.source, target=content_mention)
                outgoing_mention = get_or_create[0]

                # if it already exists, then we should reset it because 
                # there's been an update or something and it should be reprocessed.
                if not get_or_create[1]:
                    outgoing_mention.result = ""
                    outgoing_mention.success = False
                    outgoing_mention.tries = 0

                outgoing_mention.save()
            
            mention.delete()

        outgoing_webmentions = OutgoingWebmention.objects.filter(success=False).filter(tries__lt=3)

        for mention in outgoing_webmentions:
            mention.try_notify_receiver()