from feed.urlpatterns import date as date_pattern
from . import views
from django.urls import path, include

app_name = 'notes'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.DetailView.as_view(), {"wm_app_name": app_name, "wm_model_name": "Note"}, name='detail'),
]