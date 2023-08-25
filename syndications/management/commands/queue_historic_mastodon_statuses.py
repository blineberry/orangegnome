from syndications.models import MastodonStatus, MastodonStatusesToProcess,MastodonReply, MastodonBoost, MastodonFavourite
from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError, CommandParser

class Command(BaseCommand):
    def get_7days_ago_ids(self):
        seven_days_ago = (timezone.now() - timezone.timedelta(days=7)).date()

        ids = list()
        ids.extend(MastodonStatus.objects.filter(created_at__date=seven_days_ago).values_list('id_str', flat=True))
        ids.extend(MastodonReply.objects.filter(created_at__date=seven_days_ago).values_list('in_reply_to_id_str', flat=True))
        ids.extend(MastodonBoost.objects.filter(created_at__date=seven_days_ago).values_list('boost_of_id_str', flat=True))
        ids.extend(MastodonFavourite.objects.filter(created_at__date=seven_days_ago).values_list('favourite_of_id_str', flat=True))

        return ids

    def get_30days_ago_ids(self):
        thirty_days_ago = (timezone.now() - timezone.timedelta(days=30)).date()

        ids = list()
        ids.extend(MastodonStatus.objects.filter(created_at__date=thirty_days_ago).values_list('id_str', flat=True))
        ids.extend(MastodonReply.objects.filter(created_at__date=thirty_days_ago).values_list('in_reply_to_id_str', flat=True))
        ids.extend(MastodonBoost.objects.filter(created_at__date=thirty_days_ago).values_list('boost_of_id_str', flat=True))
        ids.extend(MastodonFavourite.objects.filter(created_at__date=thirty_days_ago).values_list('favourite_of_id_str', flat=True))

        return ids  

    def get_yearly_ids(self):
        now = timezone.now()

        ids = list()
        ids.extend(MastodonStatus.objects.filter(created_at__month=now.month,created_at__day=now.day).values_list('id_str', flat=True))
        ids.extend(MastodonReply.objects.filter(created_at__month=now.month,created_at__day=now.day).values_list('in_reply_to_id_str', flat=True))
        ids.extend(MastodonBoost.objects.filter(created_at__month=now.month,created_at__day=now.day).values_list('boost_of_id_str', flat=True))
        ids.extend(MastodonFavourite.objects.filter(created_at__month=now.month,created_at__day=now.day).values_list('favourite_of_id_str', flat=True))

        return ids  

    def handle(self, *args, **options):
        ids = list()

        ids.extend(self.get_7days_ago_ids())
        ids.extend(self.get_30days_ago_ids())
        ids.extend(self.get_yearly_ids())

        id_set = set(ids)
        print("queuing " + str(len(id_set)) + " statuses.")

        for id in set(ids):
            MastodonStatusesToProcess.objects.get_or_create(id_str=id)

        print(str(len(id_set)) + " statuses queued.")

    