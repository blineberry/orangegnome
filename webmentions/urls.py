from . import views
from django.urls import path

app_name = 'webmentions'
urlpatterns = [
    path('', views.IncomingWebmentionHandler.as_view(), name='webmention_handler'),
]