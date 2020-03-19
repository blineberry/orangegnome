from django.core.management.base import BaseCommand, CommandError
from posts.models import Post, Tag, Category

class Command(BaseCommand):
    help = 'Clears post data'

    def handle(self, *args, **options):
        for model in [Category, Post, Tag]:
            model.objects.all().delete()
            self.stdout.write(f'{ model._meta.verbose_name_plural } cleared')