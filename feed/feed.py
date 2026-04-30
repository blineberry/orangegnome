from django.contrib.syndication.views import Feed
from .models import FeedItem
from django.conf import settings
from django.utils import timezone

class LatestEntriesFeed(Feed):
    title = "Brent Lineberry"
    link = settings.SITE_URL
    description = "Latest entries from Brent Lineberry."
    author_name = "Brent Lineberry"
    author_link = "https://www.brentlineberry.com"
    
    def feed_copyright(self):
        return f'Copyright (c) {timezone.now().year} Brent Lineberry'

    def items(self):
        return FeedItem.objects.filter(published__lte=timezone.now()).exclude(post_type=FeedItem.PostType.LIKE).exclude(in_reply_to__isnull=False).exclude(in_reply_to='').order_by('-published')[:10]
    
    def item_title(self, item):
        return item.feed_item_header()
    
    def item_description(self, item):
        return item.feed_item_content()

    def item_link(self, item):
        return item.feed_item_link()
    
    def item_pubdate(self, item):
        return item.published