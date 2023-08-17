from django.views.generic import detail, list, dates, ListView
from .models import Tag, FeedItem
from base.views import PermalinkResponseMixin, PageTitleResponseMixin, ForceSlugMixin
from .feed import LatestEntriesFeed
from django.utils import timezone

class PublishedMultipleObjectMixin(list.MultipleObjectMixin):
    def get_queryset(self):
        return super().get_queryset().filter(published__lte=timezone.now())

class PublishedSingleObjectMixin(detail.SingleObjectMixin):
    def get_queryset(self):
        return super().get_queryset().filter(published__lte=timezone.now())

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
    template_name = 'feed/feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = None
        context['rss_title'] = LatestEntriesFeed.description
        context['rss_url'] = "%s/feed" % LatestEntriesFeed.link

        return context

class FeedItemDateArchiveView(FeedItemArchiveView):
    make_object_list = True
    template_name = 'feed/feed.html'

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
    
class TagArchive(ForceSlugMixin, PermalinkResponseMixin, detail.SingleObjectMixin, FeedItemArchiveView, PageTitleResponseMixin):
    paginate_by = 5
    template_name = 'feed/feed.html'
    canonical_viewname = 'feed:tag'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk'], self.kwargs['slug']]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Tag.objects.all())
        
        return super().get(request, *args, **kwargs)

    def get_page_title(self, context):
        return self.object.name

    def get_queryset(self):
        return self.object.feed_items.filter(published__lte=timezone.now()).order_by('-published')
    
class TagIndex(ListView, PageTitleResponseMixin):
    model = Tag
    template_name = 'feed/tags.html'
    ordering = ['name']
