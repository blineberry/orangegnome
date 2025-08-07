from typing import Any
from django.db.models.query import QuerySet
from .models import Bookmark
from django.views import generic
from base.views import PermalinkResponseMixin
from django.utils import timezone
from webmentions.views import WebmentionableMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    canonical_viewname = 'bookmarks:index'
    extra_context = {
        'page_title': 'Links | Brent Lineberry',
        'feed_title': 'Links',
    }
    paginate_by = 5

    def get_queryset(self):
        return Bookmark.objects.filter(published__lte=timezone.now()).order_by('-published')

class DetailView(WebmentionableMixin, PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'bookmarks:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Bookmark.objects
        
        return Bookmark.objects.filter(published__lte=timezone.now())
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["page_title"] = f'{self.get_object().title_txt()} | Bookmarked by Brent Lineberry'
        return context
