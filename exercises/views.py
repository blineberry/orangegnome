from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import render
from base.views import PermalinkResponseMixin
from django.views import generic
from .models import Exercise
from datetime import datetime
from django.utils import timezone

# Create your views here.
class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    date_field = 'published'
    canonical_viewname = 'exercises:index'
    extra_context = {
        'page_title': 'Exercises',
        'feed_title': 'Exercises',
    }
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Any]:
        return Exercise.objects.filter(published__lte=timezone.now()).order_by('-published')

class DetailView(PermalinkResponseMixin, generic.detail.DetailView):
    canonical_viewname = 'exercises:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk']]
    
    def get_queryset(self) -> QuerySet[Any]:
        return Exercise.objects.filter(published__lte=timezone.now())