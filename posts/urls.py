from django.urls import path

from . import views

app_name = 'posts'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/<slug:slug>', views.detail, name='detail'),
    path('category/<int:id>/<slug:slug>', views.category, name='category'),
    path('tag/<int:id>/<slug:slug>', views.tag, name='tag'),
    path('date/<int:year>/<int:month>/<int:day>', views.day, name='day'),
    path('date/<int:year>/<int:month>', views.month, name='month'),
    path('date/<int:year>', views.year, name='year'),
]