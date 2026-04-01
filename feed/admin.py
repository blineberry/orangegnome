from django.contrib import admin
from .models import Tag, Syndication, Image, PostImage, FeedItem as Post, Bookmark, Like, Note, Photo, Article
from django import forms
from django.utils import timezone
from syndications.admin import SyndicatableAdmin as SAAdmin
from feed.widgets import PlainTextCountTextarea, PlainTextCountTextInput

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
    pass

class BookmarkModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    title_md = forms.CharField(
        widget=PlainTextCountTextInput(max=Post.get_title_max(Post.PostType.BOOKMARK)),
        required=False)
    #title = CharField(widget=TextInput)

    quote_md = forms.CharField(
        widget=PlainTextCountTextarea(max=Post.get_quote_max(Post.PostType.BOOKMARK)), 
        required=False)
    """Display the quote input as a Textarea"""

    content_md = forms.CharField(
        widget=PlainTextCountTextarea(max=Post.get_content_max(Post.PostType.BOOKMARK)), 
        required=False)
    """Display the content input as a Textarea"""

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
class BookmarkAdmin(SyndicatableAdmin):
    """
    Specifications for the Bookmark Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = BookmarkModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

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

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    list_display = ['url', 'title_txt']
    """The fields to display on the admin list view."""
       
class LikeModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

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
class LikeAdmin(SyndicatableAdmin):
    """
    Specifications for the Like Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = LikeModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

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

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    list_display = ['url',]
    """The fields to display on the admin list view."""

class NoteModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.NOTE)

    content_md = forms.CharField(widget=PlainTextCountTextarea(max=Post.get_content_max(Post.PostType.NOTE)), help_text="Markdown supported.")
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
class NoteAdmin(SyndicatableAdmin):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = NoteModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

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

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """    

class PhotoModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.PHOTO)

    content_md = forms.CharField(widget=PlainTextCountTextarea(max=Post.get_content_max(Post.PostType.PHOTO)), required=False, help_text="Markdown supported.")
    """Display the caption input as a Textarea"""

    alternative_text = forms.CharField(widget=forms.Textarea, required=False)
    """Display the caption input as a Textarea"""

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
class PhotoAdmin(SyndicatableAdmin):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = PhotoModelForm
    """Override the dynamically created form with customizations."""

    inlines = [PostImageInline]

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

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

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    list_display = ['image_tag', 'content_md']

class ArticleModelForm(forms.ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    post_type = forms.CharField(widget=forms.HiddenInput, initial=Post.PostType.ARTICLE)
    
    summary_md = forms.CharField(widget=PlainTextCountTextarea(max=Post.get_summary_max(Post.PostType.ARTICLE)), help_text="Markdown supported.", required=False)
    title_md = forms.CharField(widget=PlainTextCountTextInput(max=Post.get_title_max(Post.PostType.ARTICLE)), help_text="Markdown supported.")
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

class ArticleAdmin(SyndicatableAdmin):
    form = ArticleModelForm

    prepopulated_fields = { 'slug': ('title_md',)}
    readonly_fields = ('syndicated_to_mastodon',)
    
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

    filter_horizontal = ('tags',)

# Register your models here.
admin.site.register(Article, ArticleAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Image,ImageAdmin)
admin.site.register(Post,PostAdmin)