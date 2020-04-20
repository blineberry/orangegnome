from django.urls import path, include
from feed.urlpatterns import date as date_pattern
from . import views
from django.views.generic import RedirectView

app_name = 'posts'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/<slug:slug>', views.DetailView.as_view(), name='detail'),
    path('category/<int:pk>/<slug:slug>', views.CategoryView.as_view(), name='category'),
    path('tag/<int:pk>/<slug:slug>', RedirectView.as_view(pattern_name='feed:tag'), name='tag'),    
    path('date/<int:year>/', include([
        path('', RedirectView.as_view(pattern_name='feed:year')),
        path('<int:month>/', include([
            path('', RedirectView.as_view(pattern_name='feed:month')),
            path('<int:day>', RedirectView.as_view(pattern_name='feed:day'))
        ])),
    ])),
]