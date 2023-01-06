from .models import Photo
from django.views import generic
from base.views import PermalinkResponseMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Photo.objects.filter(is_published=True)
    canonical_viewname = 'photos:index'
    extra_context = {
        'page_title': 'Photos',
        'feed_title': 'Photos',
    }
    paginate_by = 5

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    queryset = Photo.objects.filter(is_published=True)
    canonical_viewname = 'photos:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
