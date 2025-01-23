from django.views.generic import detail, list, dates, ListView, View
from .models import Tag, FeedItem, convert_commonmark_to_html, convert_commonmark_to_plain_text
from base.views import PermalinkResponseMixin, PageTitleResponseMixin, ForceSlugMixin
from .feed import LatestEntriesFeed
from django.utils import timezone
import json
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.contrib.admin.views.decorators import staff_member_required

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
        'page_title': 'Brent Lineberry',
    }
    template_name = 'feed/feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = None
        context['rss_title'] = LatestEntriesFeed.description
        context['rss_url'] = "%s/feed" % LatestEntriesFeed.link

        return context    

    def get_queryset(self):
        return super().get_queryset().filter(published__lte=timezone.now()).exclude(like__isnull=False).order_by('-published')

class FeedItemDateArchiveView(FeedItemArchiveView):
    make_object_list = True
    template_name = 'feed/feed.html'

class YearView(PermalinkResponseMixin, dates.YearArchiveView, FeedItemDateArchiveView, PageTitleResponseMixin):    
    canonical_viewname = 'feed:year'
    
    def get_canonical_view_args(self, context):
        return [context['year'].strftime("%Y")]

    def get_page_title(self, context):
        return '{d.year} Archives | Brent Lineberry'.format(d = context['year'])


class MonthView(PermalinkResponseMixin, dates.MonthArchiveView, FeedItemDateArchiveView, PageTitleResponseMixin):
    canonical_viewname = 'feed:month'
    month_format = '%m'
    
    def get_canonical_view_args(self, context):
        return [context['month'].strftime("%Y"), context['month'].strftime("%m")]

    def get_page_title(self, context):
        return '{d:%B} {d.year} Archives | Brent Lineberry'.format(d = context['month'])

class DayView(PermalinkResponseMixin, dates.DayArchiveView, FeedItemDateArchiveView, PageTitleResponseMixin):
    canonical_viewname = 'feed:day'
    month_format = '%m'
    
    def get_canonical_view_args(self, context):
        return [context['day'].strftime("%Y"), context['day'].strftime("%m"), context['day'].strftime("%d")]

    def get_page_title(self, context):
        return '{d:%B} {d.day}, {d.year} Archives | Brent Lineberry'.format(d = context['day'])
    
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
        
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["page_title"] = f'{self.object.name} | Brent Lineberry'
        return context
    
class TagIndex(ListView, PageTitleResponseMixin):
    model = Tag
    template_name = 'feed/tags.html'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["page_title"] = 'Tags | Brent Lineberry'
        return context

@method_decorator([staff_member_required, csrf_exempt], name='dispatch')
class CommonmarkConversion(View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        id = request.GET.get("id")

        if id is None:
            return HttpResponse("id parameter is required", status=400)
        
        conversion = request.session.get(id)

        if conversion is None:
            return HttpResponse("id not found", status=404)
        
        return JsonResponse(conversion)

    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)

        input = body.get("input")

        if input is None:
            return HttpResponse("input property is required", status=400)
        
        id = str(uuid.uuid4())

        request.session[id] = {
            "input": input,
            "html": convert_commonmark_to_html(input),
            "plain": convert_commonmark_to_plain_text(input)
        }

        return JsonResponse({
            "success": True,
            "id": id
        })