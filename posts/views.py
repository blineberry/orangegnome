from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag
from django.views import generic
from datetime import date
from django.http import Http404
from django.core.paginator import Paginator
from django.urls import reverse

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

class IndexView(generic.ListView):
    queryset = Post.objects.filter(is_published=True).order_by('-published')
    extra_context = {
        'title': 'Posts',
        'page_title': 'Posts'
    }
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permalink'] = self.request.build_absolute_uri(reverse('posts:index'))
        return context

class ForceSlugView(generic.View):
    def render_to_response(self, context, **response_kwargs):
        if context['object'].slug == self.kwargs['slug']:
            return super().render_to_response(context, **response_kwargs)
    
        return redirect(context['object'], permanent=True)

class DetailView(ForceSlugView, generic.DetailView):
    model = Post

    def get_object(self, queryset=None):
        return super().get_object(Post.objects.filter(is_published=True))

class CategoryView(ForceSlugView, generic.detail.SingleObjectMixin, generic.ListView):
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Category.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.posts.filter(is_published=True).order_by('published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permalink'] = self.request.build_absolute_uri(reverse('posts:category', args=[context['object'].id,context['object'].slug]))
        context['page_title'] = context['object'].name
        context['title'] = context['object'].name
        return context

class TagView(ForceSlugView, generic.detail.SingleObjectMixin, generic.ListView):
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Tag.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.posts.filter(is_published=True).order_by('published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permalink'] = self.request.build_absolute_uri(reverse('posts:tag', args=[context['object'].id,context['object'].slug]))
        context['page_title'] = context['object'].name
        context['title'] = context['object'].name
        return context