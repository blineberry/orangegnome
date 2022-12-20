from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import FeedItem
from django.conf import settings

class LatestEntriesFeed(Feed):
    title = "Orange Gnome"
    link = settings.SITE_URL
    description = "Latest entries from Brent Lineberry."

    def items(self):
        return FeedItem.objects.order_by('-published')[:5]
    
    def item_title(self, item):
        return item.feed_item_header()
    
    def item_description(self, item):
        return item.feed_item_content()

    def item_link(self, item):
        return item.get_permalink()