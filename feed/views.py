from django.shortcuts import render
from posts.models import Post
from notes.models import Note
from django.views.generic import ListView, detail, list, dates, detail
from django.db.models import Value, CharField
from itertools import chain
from django.core.paginator import Paginator
from datetime import date
from .models import Tag, FeedItem
from base.views import PermalinkResponseMixin, PageTitleResponseMixin, ForceSlugMixin

class PublishedMultipleObjectMixin(list.MultipleObjectMixin):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class PublishedSingleObjectMixin(detail.SingleObjectMixin):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class FeedItemArchiveView(PublishedMultipleObjectMixin, dates.ArchiveIndexView):
    model = FeedItem
    date_field = 'published'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = context['page_title']

        return context

class IndexView(PermalinkResponseMixin, FeedItemArchiveView):
    canonical_viewname = 'feed:index'
    extra_context = {
        'page_title': 'Orange Gnome',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = None

        return context

class FeedItemDateArchiveView(FeedItemArchiveView):
    make_object_list = True
    template_name = 'feed/feeditem_archive.html'

class YearView(PermalinkResponseMixin, dates.YearArchiveView, FeedItemDateArchiveView, PageTitleResponseMixin):    
    canonical_viewname = 'feed:year'
    
    def get_canonical_view_args(self, context):
        return [context['year'].strftime("%Y")]

    def get_page_title(self, context):
        return '{d.year} Archives'.format(d = context['year'])


class MonthView(PermalinkResponseMixin, dates.MonthArchiveView, FeedItemDateArchiveView, PageTitleResponseMixin):
    canonical_viewname = 'feed:month'
    month_format = '%m'
    
    def get_canonical_view_args(self, context):
        return [context['month'].strftime("%Y"), context['month'].strftime("%m")]

    def get_page_title(self, context):
        return '{d:%B} {d.year} Archives'.format(d = context['month'])

class DayView(PermalinkResponseMixin, dates.DayArchiveView, FeedItemDateArchiveView, PageTitleResponseMixin):
    canonical_viewname = 'feed:day'
    month_format = '%m'
    
    def get_canonical_view_args(self, context):
        return [context['day'].strftime("%Y"), context['day'].strftime("%m"), context['day'].strftime("%d")]

    def get_page_title(self, context):
        return '{d:%B} {d.day}, {d.year} Archives'.format(d = context['day'])

class TagView(ForceSlugMixin, PermalinkResponseMixin, detail.SingleObjectMixin, FeedItemArchiveView, PageTitleResponseMixin):#FeedWithTitleView):
    paginate_by = 5
    template_name = 'feed/feeditem_archive.html'
    canonical_viewname = 'feed:tag'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk'], self.kwargs['slug']]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Tag.objects.all())
        
        return super().get(request, *args, **kwargs)

    def get_page_title(self, context):
        return self.object.name

    def get_queryset(self):
        return self.object.feed_items.filter(is_published=True).order_by('-published')
