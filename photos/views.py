from .models import Photo
from django.views import generic
from base.views import PermalinkResponseMixin
from datetime import datetime

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Photo.objects.filter(published__lte=datetime.now())
    canonical_viewname = 'photos:index'
    extra_context = {
        'page_title': 'Photos',
        'feed_title': 'Photos',
    }
    paginate_by = 5

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'photos:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Photo.objects
        
        return Photo.objects.filter(published__lte=datetime.now())
