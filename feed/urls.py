from django.urls import path, include
from . import views
from .feed import LatestEntriesFeed
from django.views.generic import RedirectView

app_name = 'feed'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('date/<int:year>/', include([
        path('', views.YearView.as_view(), name='year'),
        path('<int:month>/', include([
            path('', views.MonthView.as_view(), name='month'),
            path('<int:day>', views.DayView.as_view(), name='day')
        ])),
    ])),
    path('tags/', views.TagIndex.as_view(), name='tagindex'),
    path('tags/<int:pk>/<slug:slug>', views.TagArchive.as_view(), name='tag'),
    path('tag/<int:pk>/<slug:slug>', RedirectView.as_view(permanent=True, pattern_name='feed:tag'), name='tag_old'),
    path('feed', LatestEntriesFeed())
]