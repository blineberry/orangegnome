from feed.urlpatterns import date as date_pattern
from . import views
from django.urls import path, include

app_name = 'notes'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>', views.detail, name='detail'),
    path('date/', include(date_pattern(views))),
]