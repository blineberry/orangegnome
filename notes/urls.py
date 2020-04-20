from feed.urlpatterns import date as date_pattern
from . import views
from django.urls import path, include

app_name = 'notes'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.DetailView.as_view(), name='detail'),
]