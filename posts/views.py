from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category
from django.views import generic
from datetime import date
from django.http import Http404
from django.core.paginator import Paginator
from django.urls import reverse
from base.views import ForceSlugMixin
from feed.views import PermalinkResponseMixin, PageTitleResponseMixin

def render_index(request, posts, title, permalink):
    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': title,
        'feed': page_obj,
        'page_title': title,
        'permalink': permalink
    }

    return render(request, 'posts/index.html', context)

class IndexView(PermalinkResponseMixin, generic.dates.ArchiveIndexView):
    queryset = Post.objects.filter(is_published=True)
    extra_context = {
        'feed_title': 'Posts',
        'page_title': 'Posts'
    }
    paginate_by = 5
    date_field = 'published'
    canonical_viewname = 'posts:index'

class DetailView(PermalinkResponseMixin, ForceSlugMixin, generic.DetailView):
    queryset = Post.objects.filter(is_published=True)
    canonical_viewname = 'posts:detail'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk'], self.kwargs['slug']]

class CategoryView(ForceSlugMixin, PermalinkResponseMixin, generic.detail.SingleObjectMixin, generic.ListView, PageTitleResponseMixin):
    paginate_by = 5
    template_name = 'posts/post_archive.html'
    canonical_viewname = 'posts:category'

    def get_canonical_view_args(self, context):
        return [self.kwargs['pk'], self.kwargs['slug']]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Category.objects.all())
        
        return super().get(request, *args, **kwargs)

    def get_page_title(self, context):
        return self.object.name

    def get_queryset(self):
        return self.object.posts.filter(is_published=True).order_by('-published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feed_title'] = context['page_title']

        return context