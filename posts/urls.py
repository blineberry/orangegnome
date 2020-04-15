from django.urls import path, include
from feed.urlpatterns import date as date_pattern
from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/<slug:slug>', views.detail, name='detail'),
    path('category/<int:id>/<slug:slug>', views.category, name='category'),
    path('tag/<int:id>/<slug:slug>', views.tag, name='tag'),    
    path('date/', include(date_pattern(views))),
]