from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import date
from django.views import generic
from base.views import PermalinkResponseMixin

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    queryset = Note.objects.filter(is_published=True)
    canonical_viewname = 'notes:index'
    extra_context = {
        'page_title': 'Notes',
        'feed_title': 'Notes',
    }

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    queryset = Note.objects.filter(is_published=True)
    canonical_viewname = 'notes:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
        