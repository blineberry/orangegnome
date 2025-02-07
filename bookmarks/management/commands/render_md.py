from bookmarks.models import Bookmark
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

class Command(BaseCommand):
    help = "Saves all bookmarks, prompting a render of markdown to txt and html"
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        bookmarks = Bookmark.objects.filter(
            ((Q(commentary_txt="") | Q(commentary_html="")) & ~Q(commentary_md="")) | 
            ((Q(quote_txt="") | Q(quote_html="")) & ~Q(quote_md="")) |
            ((Q(title_txt="") | Q(title_html="")) & ~Q(title_md="")))
        
        self.stdout.write(f"{len(bookmarks)} bookmarks to render.")

        for bookmark in bookmarks:
            self.stdout.write(str(bookmark.pk))
            bookmark.commentary_md.pre_save()
            self.stdout.write(bookmark.commentary_txt)
            bookmark.save()
            
        self.stdout.write("Bookmarks rendered.")