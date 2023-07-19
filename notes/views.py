from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import date, datetime
from django.views import generic
from base.views import PermalinkResponseMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Note.objects.filter(published__lte=datetime.now())
    canonical_viewname = 'notes:index'
    extra_context = {
        'page_title': 'Notes',
        'feed_title': 'Notes',
    }
    paginate_by = 5


class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'notes:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Note.objects
        
        return Note.objects.filter(published__lte=datetime.now())
