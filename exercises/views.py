from django.shortcuts import render
from base.views import PermalinkResponseMixin
from django.views import generic
from .models import Exercise

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Exercise.objects.filter(is_published=True)
    canonical_viewname = 'exercises:index'
    extra_context = {
        'page_title': 'Exercises',
        'feed_title': 'Exercises',
    }
    paginate_by = 5

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    queryset = Exercise.objects.filter(is_published=True)
    canonical_viewname = 'exercises:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]