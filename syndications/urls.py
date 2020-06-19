from . import views
from django.urls import path, include

app_name = 'syndications'
urlpatterns = [
    path('strava/webhook', views.StravaWebhookView.as_view(), name='strava_webhook'),
]