from django.shortcuts import render
from profiles.models import Profile
from notes.models import Note
from posts.models import Post
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse
from django.db.models import Value, CharField
from django.views.generic import ListView

# Create your views here.
def home(request):
    recent = Post.objects.annotate(
        type=Value('post',output_field=CharField()
    )).values(
        'pk', 'published','type',
    ).union(
        Note.objects.annotate(
            type=Value('note', output_field=CharField()
        )).values(
            'pk', 'published','type'
        )
    ).order_by('-published')

    paginator = Paginator(recent, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for obj in page_obj:
        if obj['type'] == 'post':
            obj = Post.objects.get(pk=obj['pk'])
            continue

        if obj['type'] == 'note':
            obj = Note.objects.get(pk=obj['pk'])
            continue
            
    print(page_obj.object_list)
    return

    context = {
        'feed': page_obj,
        'permalink': request.build_absolute_uri(reverse('home')),
        'page_title': settings.SITE_NAME,
    }

    return render(request, 'home/home.html', context)