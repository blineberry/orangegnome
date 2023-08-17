from . import views
from django.urls import path

app_name = 'photos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.DetailView.as_view(), {"wm_app_name": app_name, "wm_model_name": "Photo"}, name='detail'),
]