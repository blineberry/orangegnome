from .models import Note
from django.views import generic
from base.views import PermalinkResponseMixin
from django.utils import timezone
from webmentions.views import WebmentionableMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    canonical_viewname = 'notes:index'
    extra_context = {
        'page_title': 'Notes | Brent Lineberry',
        'feed_title': 'Notes',
    }
    paginate_by = 5

    def get_queryset(self):
        return Note.objects.filter(published__lte=timezone.now()).order_by('-published')


class DetailView(WebmentionableMixin, PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'notes:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Note.objects
        
        return Note.objects.filter(published__lte=timezone.now())
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["page_title"] = f'A Note from Brent Lineberry'
        return context
