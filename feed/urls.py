from django.urls import path, include
from . import views

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
    path('tag/<int:pk>/<slug:slug>', views.TagView.as_view(), name='tag'),
]