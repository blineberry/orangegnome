from datetime import datetime

from django.urls import reverse
from django.views.generic import TemplateView, detail, dates, ListView, View
from django.views.generic.list import MultipleObjectMixin
from django.shortcuts import redirect

from feed.viewmodels import AuthorVM, EntryVM, FeedVM, LinkVM, PostFeedVM
from orangegnome import settings
from profiles.models import Profile
from .models import Tag, Post as Post, convert_commonmark_to_html, convert_commonmark_to_plain_text
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

class PublishedMultipleObjectMixin(MultipleObjectMixin):
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
    allow_empty = True
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
        context['is_home'] = True
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
            try:
                self.after = timezone.datetime.fromisoformat(request.GET.get("after")).isoformat()
            except Exception as e:
                print(e)
                self.after = None
        else:
            try:
                self.before = timezone.datetime.fromisoformat(request.GET.get("before")).isoformat()
            except:
                self.before = None

    def get_viewname(self):
        return self.viewname

    def get_dt_format(self):
        return self.dt_format
    
    def dt_paginate_queryset(self, queryset:QuerySet[Post], page_size:int, viewname:str)->tuple[QuerySet[Post],str,str,str,str]:
        prev_url = None
        prev_text = None
        next_url = None
        next_text = None

        if queryset.count() <= 0:
            return (queryset, prev_url, prev_text, next_url, next_text)
        
        try:
            before = timezone.datetime.fromisoformat(self.before)
        except:
            before = None
        
        try:
            after = timezone.datetime.fromisoformat(self.after)
        except:
            after = None

        filter_args = {}
        if before is not None:
            filter_args[f'{self.get_order_field()}__lt'] = self.before
        if after is not None:
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
                next_query["after"] = last.published.isoformat()
            else:
                next_query["before"] = last.published.isoformat()
            next_url = reverse(viewname, query=next_query)

        if before is None and after is None:
            return (page, prev_url, prev_text, next_url, next_text)
        
        filter_args = {}

        if self.order == self.ORDER_ASC:
            filter_args[f'{self.get_order_field()}__lte'] = after
        else: 
            filter_args[f'{self.get_order_field()}__gte'] = before

        previous_qs = queryset.filter(**filter_args)

        previous = previous_qs.reverse()[:page_size + 1]
        previous_count = previous.count()

        # has previous
        if previous_count > 0:
            prev_text = "Load older" if self.order == self.ORDER_ASC else "Load newer"

            prev_query = self.get_base_query()

            if previous_count > page_size:
                dt = list(previous)[-1].published
                prev_key = "after" if self.order == self.ORDER_ASC else "before"
                prev_query[prev_key] = dt.isoformat()
                prev_url = reverse(viewname, query=prev_query)
            else: 
                prev_url = reverse(viewname, query=prev_query)

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

    def get_current(self, viewname):
        query = self.get_base_query()
        text = ""
        if self.get_order() == self.ORDER_ASC:
            text = "After"
        
            if self.after is not None:
                text += f' {timezone.datetime.fromisoformat(self.after).strftime(self.get_dt_format())}'
                query["after"] = self.after
        elif self.before is not None:
            text = f'Before {timezone.datetime.fromisoformat(self.before).strftime(self.get_dt_format())}'
            query["before"] = self.before

        url = reverse(viewname, query=query)
        return (url, text,)
    
    def get_first_page_url(self, context):
        query = self.get_base_query()

        return reverse(self.get_viewname(context), query=query)
    
    def get_context_data(self, **kwargs):
        paginate_by = self.paginate_by
        self.paginate_by = None
        context = super().get_context_data(**kwargs)
        self.paginate_by = paginate_by

        queryset = context.get("object_list")
        viewname = self.get_viewname(context)
        context["object_list"], context["prev_url"], context["prev_text"], context["next_url"], context["next_text"] = self.dt_paginate_queryset(queryset, self.paginate_by, viewname)
        context["cur_url"], context['cur_text'] = self.get_current(viewname)
        return context

class FeedView(DTListView):
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
        
class PostIndex(PermalinkResponseMixin, FeedView):
    post_type = None
    extra_context = {
        'page_title': 'Posts | Brent Lineberry',
        'feed_title': 'Posts',
    }
    paginate_by = 10
    order_field = 'published'
    model = Post
    full_feed = False

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

        return reverse(self.get_viewname(context), query=query)
    

    def get_base_query(self):
        query = super().get_base_query()
        
        if self.full_feed:
            query["full"] = True

        return query
        

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if request.GET.get("full", False):
            self.full_feed = True

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
        context['feed'].name = context['page_title']

        postfeed = PostFeedVM.from_feedvm(context['feed'])
        postfeed.posts = context["object_list"]
        postfeed.full = self.full_feed

        cur_url, cur_text = self.get_current(self.get_viewname(context))

        if cur_text is not None and cur_text.strip() != "":
            postfeed.subtitle = cur_text

        context["postfeed"] = postfeed 
        return context
    
    def get_viewname(self, context)->str:
        return self.get_canonical_viewname(context)

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

        if self.post_type is not None:
            qs = qs.filter(post_type=self.post_type)

        qs = qs.filter(published__lte=timezone.now())
        
        return qs

        
    
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