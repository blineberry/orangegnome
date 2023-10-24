from .models import Like
from django.views import generic
from base.views import PermalinkResponseMixin
from django.utils import timezone
from webmentions.views import WebmentionableMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    canonical_viewname = 'likes:index'
    extra_context = {
        'page_title': 'Likes | Brent Lineberry',
        'feed_title': 'Likes',
    }
    paginate_by = 5

    def get_queryset(self):
        return Like.objects.filter(published__lte=timezone.now()).order_by('-published')

class DetailView(WebmentionableMixin, PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'likes:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Like.objects
        
        return Like.objects.filter(published__lte=timezone.now())
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["page_title"] = f'{self.get_object().url} | Liked by Brent Lineberry'
        return context
