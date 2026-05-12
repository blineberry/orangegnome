from django.urls import path, include
from . import views

app_name = 'indieauth'
urlpatterns = [
    path('auth', views.AuthView.as_view(), name='auth'),
    path('token', views.TokenView.as_view(), name='token'),
    path('introspect', views.TokenView.as_view(), name='introspect'),
    path('token/revoke', views.RevokeView.as_view(), name='revoke'),
]