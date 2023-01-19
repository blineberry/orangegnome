from .models import Bookmark
from django.views import generic
from base.views import PermalinkResponseMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Bookmark.objects.filter(is_published=True)
    canonical_viewname = 'bookmarks:index'
    extra_context = {
        'page_title': 'Links',
        'feed_title': 'Links',
    }
    paginate_by = 5

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    queryset = Bookmark.objects.filter(is_published=True)
    canonical_viewname = 'bookmarks:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
