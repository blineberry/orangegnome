from django.core.management.base import BaseCommand, CommandError
from exercises.models import Exercise


class Command(BaseCommand):
    help = "Deletes stored Exercises"
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Exercise.objects.all().delete()
        self.stdout.write("Exercises deleted")