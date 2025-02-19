from bookmarks.models import Bookmark
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, F
from datetime import timedelta

class Command(BaseCommand):
    help = "Saves all bookmarks, prompting a render of markdown to txt and html"
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        bookmarks = Bookmark.objects.filter(
            Q(updated=None) | 
            Q(commonmark_rendered_at=None) |
            Q(commonmark_rendered_at__lt=F("updated") - timedelta(seconds=1))
        )
        
        self.stdout.write(f"{len(bookmarks)} bookmarks to render.")

        for bookmark in bookmarks:
            self.stdout.write(str(bookmark.pk))
            bookmark.render_commonmark_fields()
            bookmark.save()
            
        self.stdout.write("Bookmarks rendered.")