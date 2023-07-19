from .models import Bookmark
from django.views import generic
from base.views import PermalinkResponseMixin
from datetime import datetime

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Bookmark.objects.filter(published__lte=datetime.now())
    canonical_viewname = 'bookmarks:index'
    extra_context = {
        'page_title': 'Links',
        'feed_title': 'Links',
    }
    paginate_by = 5

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'bookmarks:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Bookmark.objects
        
        return Bookmark.objects.filter(published__lte=datetime.now())
