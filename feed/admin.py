from django.contrib import admin
from .models import Tag, Syndication, Image, PostImage, FeedItem as Post, Bookmark, Like, Note, Photo, Article, Repost
from django import forms
from django.utils import timezone
from syndications.admin import SyndicatableAdmin as SAAdmin
from feed.widgets import PlainTextCountTextarea, PlainTextCountTextInput
from django.core.validators import URLValidator

# Register your models here.
class SyndicationInline(admin.TabularInline):
    model = Syndication
    extra = 1

class PublishableMixin():
    is_published = 'is_published'
    published_date = 'published'

    def should_publish(self, request, obj, form, change):
        if not getattr(obj, self.is_published):
            return False

        if self.is_published not in form.changed_data:
            return False

        return True

    def publish(self, request, obj, form, change):
        if not self.should_publish(request, obj, form, change):
            return obj

        if getattr(obj, self.published_date) is None:
            setattr(obj,self.published_date,timezone.now())

        return obj

class PublishableAdmin(PublishableMixin, admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        get_data = super(PublishableAdmin, self).get_changeform_initial_data(request)
        
        if hasattr(request.user, "profile"):
            get_data['author'] = request.user.profile.pk
        
        return get_data
    
    def save_model(self, request, obj, form, change):
        obj = self.publish(request, obj, form, change)

        return super().save_model(request, obj, form, change)

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',)}
    readonly_fields = ('test',)
    fieldsets = ((None, { 'fields': ('name', 'slug', 'test')}),)

class SyndicatableAdmin(PublishableAdmin, SAAdmin):
    inlines = [SyndicationInline]

class PostImagesInlineForm(forms.ModelForm):
    alt = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = PostImage
        fields = ["image", "alt", "order", "feature"]

class PostImageInline(admin.StackedInline):
    model = PostImage
    form = PostImagesInlineForm
    extra = 0
    autocomplete_fields = ["image"]
    readonly_fields = ["image_tag"]
    fieldsets = (
        (None, {
            'fields': ('image_tag', 'image', 'alt', 'order', 'feature',)
        }),
    )

class ImageForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, required=False)

class ImageAdmin(admin.ModelAdmin):
    form = ImageForm
    search_fields = ["description", "image"]
    readonly_fields = ('image_tag',)
    fields = ["image_tag", "image", "description"]
    list_display = ['image_tag', 'description']
    inlines = [PostImageInline,]

class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('syndicated_to_mastodon',)

    inlines = [PostImageInline,SyndicationInline,]

    fieldsets = (
        (None, {
            'fields': ('post_type', 'in_reply_to', 'content_md', 'title_md', 'slug', 'summary_md', 'url', 'quote_md', 'source_name', 'source_author_name', 'source_author_url', 'author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    list_filter = ["published",]
    """Fields for filtering in the admin list view."""

class AdminBase(SyndicatableAdmin):
    inlines = [PostImageInline,SyndicationInline,]

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    list_filter = ["published",]
    """Fields for filtering in the admin list view."""

class BookmarkModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['url'].required = True

    title_md = forms.CharField(
        widget=PlainTextCountTextInput(max=Bookmark.title_max),
        required=False)

    quote_md = forms.CharField(
        widget=PlainTextCountTextarea(max=Bookmark.quote_max), 
        required=False)
    """Display the quote input as a Textarea"""

    content_md = forms.CharField(
        widget=PlainTextCountTextarea(max=Bookmark.content_max), 
        required=False)
    """Display the content input as a Textarea"""

    #url = forms.URLField(widget=forms.URLInput, max_length=2048,required=True, validators=[URLValidator])

    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.BOOKMARK)

    class Meta:
        model = Bookmark
        fields = [
            'url',
            'title_md',
            'in_reply_to', 
            'quote_md',
            'content_md',
            'author',
            'tags',
            'published',
            'post_type'
        ]

# Admin specs for the Bookmark model
class BookmarkAdmin(AdminBase):
    """
    Specifications for the Bookmark Admin page.

    Inherits from AdminBase
    """

    form = BookmarkModelForm
    """Override the dynamically created form with customizations."""

    fieldsets = (
        (None, {
            'fields': ('post_type', 'url', 'title_md', 'quote_md', 'content_md','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

    list_display = ['url', 'title_txt']
    """The fields to display on the admin list view."""
       
class LikeModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['url'].required = True

    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.LIKE)

    class Meta:
        model = Like
        fields = [
            'url',
            'author',
            'tags',
            'syndicate_to_mastodon', 
            'syndicated_to_mastodon',
            'published'
        ]

# Admin specs for the Like model
class LikeAdmin(AdminBase):
    """
    Specifications for the Like Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = LikeModelForm
    """Override the dynamically created form with customizations."""

    fieldsets = (
        (None, {
            'fields': ('post_type', 'url', 'author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

    list_display = ['url',]
    """The fields to display on the admin list view."""

class NoteModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.NOTE)

    content_md = forms.CharField(widget=PlainTextCountTextarea(max=Note.content_max), help_text="Markdown supported.")
    """Display the content input as a Textarea"""

    class Meta:
        model = Note
        fields = [
            'content_md',
            'in_reply_to',
            'author',
            'tags',
            'published',
            'post_type'
        ]

# Admin specs for the Note model
class NoteAdmin(AdminBase):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = NoteModelForm
    """Override the dynamically created form with customizations."""

    fieldsets = (
        (None, {
            'fields': ('post_type', 'content_md','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

class PhotoModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.PHOTO)

    content_md = forms.CharField(widget=PlainTextCountTextarea(max=Photo.content_max), required=True, help_text="Markdown supported.")
    # """Display the caption input as a Textarea"""

    class Meta:
        model = Photo
        fields = [
            'content_md',
            'in_reply_to',
            'author',
            'tags',
            'published',
            'post_type',
        ]

# Admin specs for the Photo model
class PhotoAdmin(AdminBase):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = PhotoModelForm
    """Override the dynamically created form with customizations."""

    fieldsets = (
        (None, {
            'fields': ('post_type', 'content_md','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

    list_display = ['admin_image_tag', 'content_md']

class ArticleModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.ARTICLE)
    
    summary_md = forms.CharField(widget=PlainTextCountTextarea(max=Article.summary_max), help_text="Markdown supported.", required=False)
    title_md = forms.CharField(widget=PlainTextCountTextInput(max=Article.title_max), help_text="Markdown supported.")
    content_md = forms.CharField(widget=PlainTextCountTextarea(), help_text="Markdown supported.", required=False)
    
    class Meta:
        model = Post
        fields = [
            'published',
            'syndicate_to_mastodon',
            'syndicated_to_mastodon',
            'title_md',
            'slug',
            'summary_md',
            'in_reply_to', 
            'content_md',
            'author',
            'tags',
            'post_type',
        ]

class ArticleAdmin(AdminBase):
    form = ArticleModelForm

    prepopulated_fields = { 'slug': ('title_md',)}
    
    fieldsets = (
        (None, {
            'fields': ('post_type', 'title_md','slug','summary_md','in_reply_to','content_md','author')
        }),
        ('Metadata', {
            'fields': ('tags',)
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )

class RepostModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.REPOST)

    class Meta:
        model = Repost
        fields = [
            'url',
            'content_md',
            'source_author_name',
            'source_author_url',
            'author',
            'tags',
            'syndicate_to_mastodon', 
            'syndicated_to_mastodon',
            'published',
            'post_type'
        ]

# Admin specs for the Repost model
class RepostAdmin(SyndicatableAdmin):
    """
    Specifications for the Repost Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin
    """

    form = RepostModelForm
    """Override the dynamically created form with customizations."""

    fieldsets = (
        (None, {
            'fields': ('post_type', 'url', 'source_name', 'content_md', 'source_author_name', 'source_author_url', 'author', 'tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

    list_display = ['url', 'source_author_name']
    """The fields to display on the admin list view."""

# Register your models here.
admin.site.register(Repost, RepostAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Image,ImageAdmin)
admin.site.register(Post,PostAdmin)