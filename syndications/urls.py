from . import views
from django.urls import path, include

app_name = 'syndications'
urlpatterns = [
    path('strava/webhook', views.StravaWebhookView.as_view(), name='strava_webhook'),
    path('replies/<int:pk>', views.ReplyView.as_view(), name='reply'),
    path('reposts/<int:pk>', views.RepostView.as_view(), name='repost'),
    path('likes/<int:pk>', views.LikeView.as_view(), name='like'),
    path('mastodon/listener', views.MastodonListener.as_view(), name='mastodon_listener')
]