from notes.models import Note
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Deletes all notes'

    def handle(self, *args, **options):
        Note.objects.all().delete()

        self.stdout.write('Notes deleted')