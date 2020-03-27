from django.shortcuts import render
from profiles.models import Profile
from posts.models import Post
from django.core.paginator import Paginator

def postToFeedItem(post):
    return { 
        'title': post.title,
        'link': post.get_absolute_url
    }

# Create your views here.
def home(request):
    posts = Post.objects.all().order_by('-published')

    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'feed': page_obj,
    }

    return render(request, 'home/home.html', context)