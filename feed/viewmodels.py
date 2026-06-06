from datetime import datetime

from profiles.models import Profile

from .models import Post
    
class LinkVM(object):
    url:str = None
    text:str = None

    def __init__(self, url:str=None, text:str=None):
        self.url = url
        self.text = text

class AuthorVM(object):
    name = None
    url = None
    photo_url = None

    @classmethod
    def from_profile(cls, profile:Profile):
        vm = cls()
        vm.name = profile.name
        vm.url = profile.url
        vm.photo_url = profile.photo.url

class UrlContextVM(object):
    url:str = None
    title:str = None
    author:AuthorVM = None

class EntryVM(object):
    reply_to:UrlContextVM = None
    bookmark_of:UrlContextVM = None
    like_of:UrlContextVM = None
    repost_of:UrlContextVM = None
    name:str = None
    summary:str = None
    content:str = None
    author:AuthorVM = None
    dt_published:datetime = None
    url:str = None
    categories:list[LinkVM] = None
    syndications:list[LinkVM] = None
    pass

class PageVM(object):
    page_title = ""
    permalink = ""

    @classmethod
    def from_posttype(cls, post_type:Post.PostType):
        vm = cls()

        if post_type == Post.PostType.ARTICLE: 
            vm.page_title = 'Articles | Brent Lineberry'

        if post_type == Post.PostType.BOOKMARK: 
            vm.page_title = 'Links | Brent Lineberry'
        
        if post_type == Post.PostType.LIKE: 
            vm.page_title = 'Likes | Brent Lineberry'

        if post_type == Post.PostType.NOTE: 
            vm.page_title = 'Notes | Brent Lineberry'

        if post_type == Post.PostType.PHOTO: 
            vm.page_title = 'Photos | Brent Lineberry'

        if post_type == Post.PostType.REPOST: 
            vm.page_title = 'Reposts | Brent Lineberry'

        return vm

class ImageVM(object):
    url:str = None
    alt:str = None

class FeedVM(object):
    url:str = None
    uid:str = None
    alternates:list[LinkVM] = []
    name:str = None
    author:AuthorVM = None
    photo:ImageVM = None
    prev:LinkVM = None
    next:LinkVM = None

class PostFeedVM(FeedVM):
    posts = []
    full = False
    subtitle = None

    @classmethod
    def from_feedvm(cls, vm:FeedVM):
        c = cls()
        c.url = vm.url
        c.uid = vm.uid
        c.name = vm.name
        c.author = vm.author
        c.photo = vm.photo
        c.prev = vm.prev
        c.next = vm.next
        c.alternates = vm.alternates

        return c