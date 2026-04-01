from django.urls import path, include
from . import views
from .feed import LatestEntriesFeed
from django.views.generic import RedirectView
from .models import FeedItem as Post

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
    path('tags/', views.TagIndex.as_view(), name='tagindex'),
    path('tags/<int:pk>/<slug:slug>', views.TagArchive.as_view(), name='tag'),
    path('tag/<int:pk>/<slug:slug>', RedirectView.as_view(permanent=True, pattern_name='feed:tag'), name='tag_old'),
    path('feed', LatestEntriesFeed()),
    path('api/commonmarkconversion', views.CommonmarkConversion.as_view(), name="commonmarkconversion"),
    path('posts/', views.PostIndex.as_view(), name="posts"),
    path('posts/<int:pk>', views.PostDetailView.as_view(), name="detail"),
    path('posts/<int:pk>/<slug:slug>', views.PostDetailView.as_view(), name="detail"),
    path('bookmarks/', views.PostIndex.as_view(post_type=Post.PostType.BOOKMARK), {"wm_app_name": 'feed', "wm_model_name": "FeedItem"}, name="bookmarks"),
    path('bookmarks/<int:pk>', RedirectView.as_view(permanent=True, pattern_name='feed:detail'), name='bookmarkdetail_old'),
    path('likes/', views.PostIndex.as_view(post_type=Post.PostType.LIKE), {"wm_app_name": 'feed', "wm_model_name": "FeedItem"}, name="likes"),
    path('likes/<int:pk>', RedirectView.as_view(permanent=True, pattern_name='feed:detail'), name='likedetail_old'),
    path('notes/', views.PostIndex.as_view(post_type=Post.PostType.NOTE), {"wm_app_name": 'feed', "wm_model_name": "FeedItem"}, name="notes"),
    path('notes/<int:pk>', RedirectView.as_view(permanent=True, pattern_name='feed:detail'), name='notedetail_old'),
    path('photos/', views.PostIndex.as_view(post_type=Post.PostType.PHOTO), {"wm_app_name": 'feed', "wm_model_name": "FeedItem"}, name="photos"),
    path('photos/<int:pk>', RedirectView.as_view(permanent=True, pattern_name='feed:detail'), name='photodetail_old'),
    path('articles/', views.PostIndex.as_view(post_type=Post.PostType.ARTICLE), {"wm_app_name": 'feed', "wm_model_name": "FeedItem"}, name="articles"),
    path('articles/<int:pk>/<slug:slug>', RedirectView.as_view(permanent=True, pattern_name='feed:detail'), name='photodetail_old'),
]