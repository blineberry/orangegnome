"""orangegnome URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls', namespace='posts')),
    path('notes/', include('notes.urls', namespace='notes')),
    path('exercises/', include('exercises.urls', namespace='exercises')),
    path('photos/', include('photos.urls', namespace='photos')),
    path('bookmarks/', include('bookmarks.urls', namespace='bookmarks')),
    path('syndications/', include('syndications.urls', namespace='syndications')),
    path('webmentions/', include('webmentions.urls', namespace='webmentions')),
    path('', include('feed.urls', namespace='feed')),
    path('robots.txt', TemplateView.as_view(template_name="base/robots.txt", content_type="text/plain")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
