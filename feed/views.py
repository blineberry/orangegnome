from django.views.generic import detail, list, dates, ListView, View
from .models import Tag, FeedItem as Post, convert_commonmark_to_html, convert_commonmark_to_plain_text
from base.views import PermalinkResponseMixin, PageTitleResponseMixin, ForceSlugMixin
from .feed import LatestEntriesFeed
from django.utils import timezone
import json
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.query import QuerySet
from typing import Any
from webmentions.views import WebmentionableMixin

class PublishedMultipleObjectMixin(list.MultipleObjectMixin):
    def get_queryset(self):
        return super().get_queryset().filter(published__lte=timezone.now())

class PublishedSingleObjectMixin(detail.SingleObjectMixin):
    def get_queryset(self):
        return super().get_queryset().filter(published__lte=timezone.now())

class FeedItemArchiveView(PublishedMultipleObjectMixin, dates.ArchiveIndexView):
    model = Post
    date_field = 'published'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = context['page_title']

        return context

class IndexView(PermalinkResponseMixin, FeedItemArchiveView):
    canonical_viewname = 'feed:index'
    extra_context = {
        'page_title': 'Brent Lineberry',
    }
    template_name = 'feed/post_archive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = None
        context['rss_title'] = LatestEntriesFeed.description
        context['rss_url'] = "%s/feed" % LatestEntriesFeed.link

        return context    

    def get_queryset(self):
        return super().get_queryset().filter(published__lte=timezone.now()).exclude(post_type=Post.PostType.LIKE).order_by('-published')

class FeedItemDateArchiveView(FeedItemArchiveView):
    make_object_list = True
    template_name = 'feed/post_archive.html'

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
    paginate_by = 10
    template_name = 'feed/post_archive.html'
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
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)

        input = body.get("input")
        block_content = body.get("blockContent", True)

        if input is None:
            return HttpResponse("input property is required", status=400)

        conversion = {
            "input": input,
            "html": convert_commonmark_to_html(input, block_content),
            "plain": convert_commonmark_to_plain_text(input)
        }

        return JsonResponse(conversion)
    
class PostIndex(PermalinkResponseMixin, dates.ArchiveIndexView):
    post_type = None
    extra_context = {
        'page_title': 'Posts | Brent Lineberry',
        'feed_title': 'Posts',
    }
    template_name = 'feed/post_archive.html'
    paginate_by = 10
    date_field = 'published'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title = 'Posts | Brent Lineberry'
        feed_title = 'Posts'

        if self.post_type == Post.PostType.ARTICLE: 
            page_title = 'Articles | Brent Lineberry'
            feed_title = 'Articles'

        if self.post_type == Post.PostType.BOOKMARK: 
            page_title = 'Links | Brent Lineberry'
            feed_title = 'Links'
        
        if self.post_type == Post.PostType.LIKE: 
            page_title = 'Likes | Brent Lineberry'
            feed_title = 'Likes'

        if self.post_type == Post.PostType.NOTE: 
            page_title = 'Notes | Brent Lineberry'
            feed_title = 'Notes'

        if self.post_type == Post.PostType.PHOTO: 
            page_title = 'Photos | Brent Lineberry'
            feed_title = 'Photos'

        if self.post_type == Post.PostType.REPOST: 
            page_title = 'Reposts | Brent Lineberry'
            feed_title = 'Reposts'

        context['page_title'] = page_title
        context['feed_title'] = feed_title
        return context

    def get_canonical_viewname(self, context):
        if self.post_type == Post.PostType.ARTICLE: 
            return 'feed:articles'

        if self.post_type == Post.PostType.BOOKMARK: 
            return 'feed:bookmarks'
        
        if self.post_type == Post.PostType.LIKE: 
            return 'feed:likes'

        if self.post_type == Post.PostType.NOTE: 
            return 'feed:notes'

        if self.post_type == Post.PostType.PHOTO: 
            return 'feed:photos'

        if self.post_type == Post.PostType.REPOST: 
            return 'feed:reposts'          
        
        return 'feed:posts'

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset().filter(published__lte=timezone.now())

        if self.post_type is None:
            return qs.order_by('-published')
        
        return qs.filter(post_type=self.post_type).order_by('-published')
    
class PostDetailView(ForceSlugMixin, WebmentionableMixin, PermalinkResponseMixin, detail.DetailView):
    pk = 0
    slug = None
    canonical_viewname = 'feed:detail'        
    template_name = 'feed/post_detail.html'

    def get_canonical_view_args(self, context):
        canonical_view_args = [self.pk]

        if self.slug is not None:
            canonical_view_args.append(self.slug)
        
        return canonical_view_args
    
    def get_queryset(self):
        # Allow a draft view if the user is_staff
        if self.request.user.is_staff:
            return Post.objects
        
        return Post.objects.filter(published__lte=timezone.now())
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        post = self.get_object()

        context['post'] = post
        context['permalink'] = post.get_permalink()
        context['edit_link'] = post.get_edit_link()

        if post.post_type == Post.PostType.BOOKMARK:
            context["page_title"] = f'{post.title_txt()} | Bookmarked by Brent Lineberry'

        if post.post_type == Post.PostType.LIKE:
            context["page_title"] = f'{post.url} | Liked by Brent Lineberry'
        
        if post.post_type == Post.PostType.NOTE:
            context["page_title"] = f'{post.content_txt()} | Brent Lineberry'
        
        if post.post_type == Post.PostType.PHOTO:
            context["page_title"] = f'{post.content_txt()} | Brent Lineberry'

        if post.post_type == Post.PostType.ARTICLE:
            context["page_title"] = f'{post.title_txt()} | Brent Lineberry'

        if post.post_type == Post.PostType.REPOST:
            context["page_title"] = f'{post.source_author_name} reposted by Brent Lineberry'

        return context