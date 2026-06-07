from datetime import date

from django.urls import reverse
from django.views.generic import detail, ListView, View

from feed.viewmodels import EntryVM, FeedVM, LinkVM, PostFeedVM
from .models import Image, PostImage, Tag, Post as Post, convert_commonmark_to_html, convert_commonmark_to_plain_text
from base.views import PermalinkResponseMixin, PageTitleResponseMixin, ForceSlugMixin
from .feed import LatestEntriesFeed
from django.utils import timezone
import json
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from typing import Any
from webmentions.views import WebmentionableMixin
    
class DTListView(ListView):
    ORDER_ASC = "asc"
    ORDER_DESC = "desc"
    order_field = None
    viewname = None
    order = ORDER_DESC
    paginate_by = None
    before = None
    after = None
    dt_format = '%b %-d, %Y %-I:%M %p %Z'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.order = self.ORDER_ASC if request.GET.get("order") == self.ORDER_ASC else self.ORDER_DESC

        if self.order == self.ORDER_ASC:
            self.after = self.parse_after_str(request.GET.get("after"))
        else:
            self.before = self.parse_before_str(request.GET.get("before"))

    def get_viewname(self, context):
        return self.viewname

    def get_dt_format(self):
        return self.dt_format
    
    def get_obj_order_field(self, obj):
        return obj.published
    
    def parse_order_field_str(self, s):
        try:
            return timezone.datetime.fromisoformat(s)
        except Exception as e:
            return None
    
    def parse_before_str(self, s):
        return self.parse_order_field_str(s)
    
    def parse_after_str(self, s):
        return self.parse_order_field_str(s)
        
    def before_str(self):
        return self.before.isoformat()
    
    def after_str(self):
        return self.after.isoformat()
    
    def get_obj_order_field_display(self, f):
        return f.strftime(self.get_dt_format())
        
    def before_display(self):
        return self.get_obj_order_field_display(self.before)
    
    def after_display(self):
        return self.get_obj_order_field_display(self.after)   

    
    def dt_paginate_queryset(self, queryset:QuerySet[Post], page_size:int, viewname:str, context)->tuple[QuerySet[Post],str,str,str,str]:
        prev_url = None
        prev_text = None
        next_url = None
        next_text = None

        if queryset.count() <= 0:
            return (queryset, prev_url, prev_text, next_url, next_text)
        
        filter_args = {}
        if self.before is not None:
            filter_args[f'{self.get_order_field()}__lt'] = self.before
        if self.after is not None:
            filter_args[f'{self.get_order_field()}__gt'] = self.after
        
        dt_queryset = queryset.filter(**filter_args)
        page = dt_queryset[:page_size]

        last = None 

        page_count = page.count()

        if page_count > 0:
            last = list(page)[-1]

        # has next
        if dt_queryset.count() > page_count:
            next_text = "Load newer" if self.order == self.ORDER_ASC else "Load older"
            next_query = self.get_base_query()
            if self.order == self.ORDER_ASC:
                next_query["after"] = self.get_obj_order_field(last)
            else:
                next_query["before"] = self.get_obj_order_field(last)
            next_url = reverse(viewname, args=self.get_canonical_view_args(context), query=next_query)

        if self.before is None and self.after is None:
            return (page, prev_url, prev_text, next_url, next_text)
        
        filter_args = {}

        if self.order == self.ORDER_ASC:
            filter_args[f'{self.get_order_field()}__lte'] = self.after
        else: 
            filter_args[f'{self.get_order_field()}__gte'] = self.before

        previous_qs = queryset.filter(**filter_args)

        previous = previous_qs.reverse()[:page_size + 1]
        previous_count = previous.count()

        # has previous
        if previous_count > 0:
            prev_text = "Load older" if self.order == self.ORDER_ASC else "Load newer"

            prev_query = self.get_base_query()

            if previous_count > page_size:
                of = self.get_obj_order_field(list(previous)[-1])
                prev_key = "after" if self.order == self.ORDER_ASC else "before"
                prev_query[prev_key] = self.parse_order_field_str(of)
                prev_url = reverse(viewname, args=self.get_canonical_view_args(context), query=prev_query)
            else: 
                prev_url = reverse(viewname, args=self.get_canonical_view_args(context), query=prev_query)

        return (page, prev_url, prev_text, next_url, next_text)
    
    def get_order(self):
        if self.order is not None:
            return self.order
        
        return "desc"
    
    def get_order_field(self):
        return self.order_field
    
    def get_ordering(self):
        order = self.get_order()
        return self.order_field if order == "asc" else f'-{self.order_field}'
    
    def get_base_query(self):
        query = {}
        if self.get_order() == self.ORDER_ASC:
            query["order"] = self.ORDER_ASC

        return query

    def get_current(self, viewname, context):
        query = self.get_base_query()
        text = ""
        if self.get_order() == self.ORDER_ASC:
            text = "After"
        
            if self.after is not None:
                text += f' {self.get_obj_order_field_display(self.after)}'
                query["after"] = self.after
        elif self.before is not None:
            text = f'Before {self.get_obj_order_field_display(self.before)}'
            query["before"] = self.before

        url = reverse(viewname, args=self.get_canonical_view_args(context), query=query)
        return (url, text,)
    
    def get_first_page_url(self, context):
        query = self.get_base_query()

        return reverse(self.get_viewname(context), args=self.get_canonical_view_args(context), query=query)
    
    def get_context_data(self, **kwargs):
        paginate_by = self.paginate_by
        self.paginate_by = None
        context = super().get_context_data(**kwargs)
        self.paginate_by = paginate_by

        queryset = context.get("object_list")
        viewname = self.get_viewname(context)
        context["object_list"], context["prev_url"], context["prev_text"], context["next_url"], context["next_text"] = self.dt_paginate_queryset(queryset, self.paginate_by, viewname, context)
        context["cur_url"], context['cur_text'] = self.get_current(viewname, context)
        return context

class FeedView(DTListView):
    def get_feed_alts(self,context):
        return []

    def get_uid_url(self, context):
        return None
    
    def get_url(self,context):
        return self.get_first_page_url(context)
    
    def get_name(self):
        return None
    
    def get_photo(self):
        return None
    
    def get_author(self):
        return None
    
    def object_to_entry(self, obj:object)->EntryVM:
        return EntryVM()
    
    def objects_to_entries(self, objs:list[object])->list[EntryVM]:
        return lambda o: self.object_to_entry(o)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        feed:FeedVM = FeedVM()

        feed.url = self.get_url(context)
        feed.uid = self.get_uid_url(context)
        feed.alternates = self.get_feed_alts(context)
        feed.name = self.get_name()
        feed.author = self.get_author()
        feed.photo = self.get_photo()

        if context["prev_url"]:
            feed.prev = LinkVM(url=context["prev_url"],text=context["prev_text"])
        
        if context["next_url"]:
            feed.next = LinkVM(url=context["next_url"],text=context["next_text"])
        
        feed.entries = self.objects_to_entries(context["object_list"])

        context["feed"] = feed
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
    
class PostIndex(PermalinkResponseMixin, FeedView):
    extra_context = {
        'page_title': 'Posts | Brent Lineberry',
        'feed_title': 'Posts',
    }
    paginate_by = 10
    order_field = 'published'
    model = Post
    full_feed = False
    canonical_viewname = 'feed:posts'

    def get_feed_alts(self,context):
        alts = []

        if not self.full_feed:
            return alts
        
        query = {}
        if self.order == self.ORDER_ASC:
            query["order"] = self.ORDER_ASC

        alts.append(LinkVM(url=reverse(self.get_viewname(context), args=self.get_canonical_view_args(context), query=query), text="View partial content feed"))

        return alts

    def get_uid_url(self, context):
        # if self.full_feed is True, then this is the full feed and there is no
        # need for the uid
        if self.full_feed:
            return None
        
        query = {
            "full": True
        }

        if self.order == self.ORDER_ASC:
            query["order"] = self.ORDER_ASC

        return reverse(self.get_viewname(context), args=self.get_canonical_view_args(context), query=query)
    

    def get_base_query(self):
        query = super().get_base_query()
        
        if self.full_feed:
            query["full"] = True

        return query
        

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if request.GET.get("full", False):
            self.full_feed = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed'].name = context['page_title']

        postfeed = PostFeedVM.from_feedvm(context['feed'])
        postfeed.posts = context["object_list"]
        postfeed.full = self.full_feed

        cur_url, cur_text = self.get_current(self.get_viewname(context), context)

        if cur_text is not None and cur_text.strip() != "":
            postfeed.subtitle = cur_text

        context["postfeed"] = postfeed 
        return context
    
    def get_viewname(self, context)->str:
        return self.get_canonical_viewname(context)

    def get_canonical_viewname(self, context):
        return self.canonical_viewname
    
    def get_canonical_view_query(self, context):
        query = {}

        if self.full_feed:
            query["full"] = True

        if self.get_order() == self.ORDER_ASC:
            query["order"] = self.ORDER_ASC
        
            if self.after is not None:
                query["after"] = self.after
        elif self.before is not None:
            query["before"] = self.before

        return query

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()

        qs = qs.filter(published__lte=timezone.now())
        
        return qs
        
class PostTypeIndex(PostIndex):
    post_type = None        

    def get_titles(self):
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

        return (page_title, feed_title,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'], context['feed_title'] = self.get_titles()
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
        qs = super().get_queryset()

        if self.post_type is not None:
            qs = qs.filter(post_type=self.post_type)
        
        return qs

class HomeView(PostIndex):
    allow_empty = True
    canonical_viewname = 'feed:index'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        del context['feed_title']
        context['rss_title'] = LatestEntriesFeed.description
        context['rss_url'] = "%s/feed" % LatestEntriesFeed.link
        context['is_home'] = context.get("feed") is None or context["feed"].prev is None
        context['page_title'] = 'Brent Lineberry'
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        qs.exclude(post_type=Post.PostType.LIKE)

        return qs
    
    def get_canonical_viewname(self, context):
        return self.canonical_viewname
    
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
    
class YearView(PostIndex):
    canonical_viewname = 'feed:year'
    date = None
    year = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.year = self.kwargs.get("year")
        self.date = date(self.year, 1, 1)
    
    def get_canonical_view_args(self, context):
        return [self.date.strftime("%Y")]
    
    def get_queryset(self):
        qs = super().get_queryset()

        if self.year is not None:
            qs = qs.filter(published__year=self.year)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '{d.year} Archives | Brent Lineberry'.format(d = self.date)
        context['feed_title'] = '{d.year} Archives'.format(d = self.date)

        return context
    
class MonthView(YearView):
    canonical_viewname = 'feed:month'
    month = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.month = self.kwargs.get("month")
        self.date = date(self.year, self.month, 1)
    
    def get_canonical_view_args(self, context):
        args = super().get_canonical_view_args(context)
        args.append(self.month)
        return args

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '{d:%B} {d.year} Archives | Brent Lineberry'.format(d = self.date)
        context['feed_title'] = '{d:%B} {d.year} Archives'.format(d = self.date)

        return context
    
    def get_queryset(self):
        qs = super().get_queryset()

        if self.year is not None:
            qs = qs.filter(published__month=self.month)
        
        return qs
    
class DayView(MonthView):
    canonical_viewname = 'feed:day'
    day = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.year = self.kwargs.get("year")
        self.month = self.kwargs.get("month")
        self.day = self.kwargs.get("day")

        self.date = date(self.year, self.month, self.day)
    
    def get_canonical_view_args(self, context):
        return [self.date.strftime("%Y"), self.date.strftime("%m"), self.date.strftime("%d")]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '{d:%B} {d.day}, {d.year} Archives | Brent Lineberry'.format(d = self.date)
        context['feed_title'] = '{d:%B} {d.day}, {d.year} Archives'.format(d = self.date)

        return context
    
    def get_queryset(self):
        qs = super().get_queryset()

        if self.year is not None:
            qs = qs.filter(published__day=self.day)
        
        return qs
    
class TagArchive(PostIndex):
    canonical_viewname = 'feed:tag'
    tag_id = 0

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.tag_id = self.kwargs.get("pk")

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk'], self.kwargs['slug']]

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(tags__id=self.tag_id)
        
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        tag = Tag.objects.get(pk=self.tag_id)
        context = super().get_context_data(**kwargs)
        context["page_title"] = f'{tag.name} | Brent Lineberry'
        context["feed_title"] = f'{tag.name}'
        return context
    
class PhotostreamView(PermalinkResponseMixin, FeedView):
    canonical_viewname = "feed:photostream"
    model = Image
    template_name = 'feed/photostream.html'
    order_field = 'id'
    extra_context = {
        'page_title': 'Photostream | Brent Lineberry',
        'feed_title': 'Photostream',
    }
    full_feed = False
    paginate_by = 99

    def get_obj_order_field(self, obj):
        return obj.id

    def parse_order_field_str(self, s):
        try:
            return int(s)
        except:
            return None
    
    def get_obj_order_field_display(self, f):
        return str(f)

    def get_viewname(self, context)->str:
        return self.get_canonical_viewname(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed'].name = context['page_title']

        postfeed = PostFeedVM.from_feedvm(context['feed'])
        postfeed.full = self.full_feed

        cur_url, cur_text = self.get_current(self.get_viewname(context), context)

        if cur_text is not None and cur_text.strip() != "":
            postfeed.subtitle = cur_text

        context["postfeed"] = postfeed 
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.annotate(post_count=Count('posts', filter=Q(posts__published__lte=timezone.now()))) #.filter(post_count__gt=0)
        
        return qs