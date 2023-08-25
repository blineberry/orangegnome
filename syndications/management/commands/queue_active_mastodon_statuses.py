from syndications.models import MastodonStatus, MastodonStatusesToProcess,MastodonReply, MastodonBoost, MastodonFavourite
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError, CommandParser

class Command(BaseCommand):
    def get_past_24hrs_ids(self):
        datetime = timezone.now() - timezone.timedelta(days=1)

        ids = list()
        ids.extend(MastodonStatus.objects.filter(created_at__gte=datetime).values_list('id_str', flat=True))
        ids.extend(MastodonReply.objects.filter(created_at__gte=datetime).values_list('in_reply_to_id_str', flat=True))
        ids.extend(MastodonBoost.objects.filter(created_at__gte=datetime).values_list('boost_of_id_str', flat=True))
        ids.extend(MastodonFavourite.objects.filter(created_at__gte=datetime).values_list('favourite_of_id_str', flat=True))

        return ids

    def handle(self, *args, **options):
        ids = list()


        ids.extend(self.get_past_24hrs_ids())

        id_set = set(ids)
        print("queuing " + str(len(id_set)) + " statuses.")

        for id in set(ids):
            MastodonStatusesToProcess.objects.get_or_create(id_str=id)

        print(str(len(id_set)) + " statuses queued.")

    