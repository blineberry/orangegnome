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

def index(request):
    posts = Post.objects.order_by('-published')

    return render_index(request, posts, 'Posts', request.build_absolute_uri(reverse('posts:index')))

def render_or_redirect(id, slug, model, render_func):
    item = get_object_or_404(model, pk=id)

    if item.slug != slug:
        return redirect(item, permanent=True)

    return render_func(item)
    #return render(request, template, get_context(item))

def detail(request, id, slug):
    return render_or_redirect(id, slug, Post, lambda post: render(request, 'posts/detail.html', { 'post': post, 'permalink': request.build_absolute_uri(post.get_absolute_url()) }))

def category(request, id, slug):
    return render_or_redirect(id, slug, Category, lambda category: render_index(request, category.posts.order_by('-published').all(), category.name, request.build_absolute_uri(reverse('posts:category', args=[id,slug]))))

def tag(request, id, slug):
    return render_or_redirect(id, slug, Tag, lambda tag: render_index(request, tag.posts.order_by('-published').all(), tag.name, request.build_absolute_uri(reverse('posts:tag', args=[id,slug]))))

def day(request, year, month, day):
    try:
        d = date(year, month, day)
    except ValueError:
        raise Http404("Date does not exist")

    posts = Post.objects.filter(published__year=year, published__month=month, published__day=day).order_by('-published')
    return render_index(request, posts, '{d:%B} {d.day}, {d.year} Archives'.format(d = d), request.build_absolute_uri(reverse('posts:day', args=[year,month,day])))

def month(request, year, month):
    try:
        d = date(year, month, 1)
    except ValueError:
        raise Http404("Month does not exist")

    posts = Post.objects.filter(published__year=year, published__month=month).order_by('-published')
    return render_index(request, posts, '{d:%B} {d.year} Archives'.format(d = d), request.build_absolute_uri(reverse('posts:month', args=[year,month])))

def year(request, year):
    try:
        d = date(year, 1, 1)
    except ValueError:
        raise Http404("Year does not exist")

    posts = Post.objects.filter(published__year=year).order_by('-published')
    return render_index(request, posts, '{d.year} Archives'.format(d = d), request.build_absolute_uri(reverse('posts:year', args=[year])))