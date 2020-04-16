from django.shortcuts import render
from posts.models import Post
from notes.models import Note
from django.views.generic import ListView
from django.db.models import Value, CharField
from itertools import chain
from django.core.paginator import Paginator
from datetime import date

def get_combined_recent(paginate_by, **kwargs):
    recent = Post.objects.filter(is_published=True,**kwargs).annotate(
        type=Value('post',output_field=CharField())
    ).values(
        'pk','published','type', 'is_published'
    ).union(
        Note.objects.filter(is_published=True,**kwargs).annotate(
            type=Value('note', output_field=CharField())
        ).values(
            'pk','published','type', 'is_published'
        )
    ).order_by('-published')[:(paginate_by*2)]

    records = list(recent)

    type_to_queryset = {
        'post': Post.objects.all(),
        'note': Note.objects.all(),
    }

    # Collect the pks we need to load for each type:
    to_load = {}
    for record in records:
        to_load.setdefault(record['type'], []).append(record['pk'])

    # Fetch them 
    feed_items = list()
    for type, pks in to_load.items():
        feed_items = chain(feed_items,type_to_queryset[type].filter(pk__in=pks))

    feed_items = list(feed_items)
    feed_items.sort(key=lambda e: e.published, reverse=True)
    return feed_items

class FeedView(ListView):
    template_name = 'feed/index.html'
    paginate_by = 5
    filters = {}

    def get_queryset(self):
        return get_combined_recent(self.paginate_by, **self.filters)

    class Meta:
        abstract = True

# Create your views here.
class FeedView(ListView):
    template_name = 'feed/index.html'
    paginate_by = 5
    filters = {}

    def get_queryset(self):
        return get_combined_recent(self.paginate_by, **self.filters)

class FeedWithTitleView(FeedView):
    title = ''

    def get_title(self):
        return title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = self.get_title()
        return context

class DateArchiveView(FeedWithTitleView):
    title_format_string = ''

    def set_date_from_kwargs(self):
        has_year = 'year' in self.kwargs
        has_month = 'month' in self.kwargs
        has_day = 'day' in self.kwargs

        year = 1
        month = 1
        day = 1

        if has_year:
            year = self.kwargs['year']

        if has_month:
            month = self.kwargs['month']

        if has_day:
            day = self.kwargs['day']

        try:
            self.date = date(year, month, day)
        except ValueError:
            if not has_year:
                raise Http404("Year does not exist")

            if not has_month:
                raise Http404("Month does not exist")

            raise Http404("Date does not exist")

        if has_year:
            self.filters['published__year'] = year

        if has_month:
            self.filters['published__month'] = month

        if has_day:
            self.filters['published__day'] = day

    # overriding `get` to insert methods into the lifecycle
    def get(self, request, *args, **kwargs):
        self.set_date_from_kwargs()
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_title(self):
        return self.title_format_string.format(d = self.date)

class YearView(DateArchiveView):
    title_format_string = '{d.year} Archives'

class MonthView(DateArchiveView):
    title_format_string = '{d:%B} {d.year} Archives'

class DayView(DateArchiveView):
    title_format_string = '{d:%B} {d.day}, {d.year} Archives'
