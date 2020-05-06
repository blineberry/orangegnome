from django.core.management.base import BaseCommand, CommandError
from syndications.models import StravaActivity


class Command(BaseCommand):
    help = "Deletes stored StravaActivities"
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        StravaActivity.objects.all().delete()
        self.stdout.write("StravaActivities deleted")