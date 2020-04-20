from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import date
from django.views import generic

def render_index(request, notes, title, permalink):
    paginator = Paginator(notes, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': title,
        'feed': page_obj,
        'page_title': title,
        'permalink': permalink
    }

    return render(request, 'notes/index.html', context)

# Create your views here.
class IndexView(generic.ListView):
    model = Note

def index(request):
    notes = Note.objects.filter(is_published=True).order_by('-published')

    return render_index(request, notes, 'Notes', request.build_absolute_uri(reverse('notes:index')))

def render_or_redirect(id, slug, model, render_func):
    item = get_object_or_404(model, pk=id)

    if item.slug != slug:
        return redirect(item, permanent=True)

    return render_func(item)
    #return render(request, template, get_context(item))

def detail(request, id):
    item = get_object_or_404(Note, pk=id, is_published=True)

    context = {
        'note': item,
        'permalink': request.build_absolute_uri(item.get_absolute_url())
    }
    
    return render(request, 'notes/detail.html', context)


def day(request, year, month, day):
    try:
        d = date(year, month, day)
    except ValueError:
        raise Http404("Date does not exist")

    notes = Note.objects.filter(published__year=year, published__month=month, published__day=day).order_by('-published')
    return render_index(request, notes, '{d:%B} {d.day}, {d.year} Archives'.format(d = d), request.build_absolute_uri(reverse('notes:day', args=[year,month,day])))

def month(request, year, month):
    try:
        d = date(year, month, 1)
    except ValueError:
        raise Http404("Month does not exist")

    notes = Note.objects.filter(published__year=year, published__month=month).order_by('-published')
    return render_index(request, notes, '{d:%B} {d.year} Archives'.format(d = d), request.build_absolute_uri(reverse('notes:month', args=[year,month])))

def year(request, year):
    try:
        d = date(year, 1, 1)
    except ValueError:
        raise Http404("Year does not exist")

    notes = Note.objects.filter(published__year=year).order_by('-published')
    return render_index(request, notes, '{d.year} Archives'.format(d = d), request.build_absolute_uri(reverse('notes:year', args=[year])))