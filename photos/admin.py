from django.contrib import admin, messages
from django.http import HttpRequest
from feed.widgets import PlainTextCountTextarea
from .models import Photo
from feed.admin import SyndicatableAdmin
from django.forms import ModelForm, CharField, Textarea
from feed.models import PostImage

# Customize the Admin form
class ImagesInlineForm(ModelForm):
    alt = CharField(widget=Textarea, required=False)

    class Meta:
        model = PostImage
        fields = ["image", "alt", "order", "feature"]


class ImagesInline(admin.StackedInline):
    model = PostImage
    form = ImagesInlineForm
    extra = 0
    autocomplete_fields = ["image"]
    readonly_fields = ["image_tag"]
    fieldsets = (
        (None, {
            'fields': ('image_tag', 'image', 'alt', 'order', 'feature',)
        }),
    )

class PhotoModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    content_md = CharField(widget=PlainTextCountTextarea(max=Photo.content_max), required=False, help_text="Markdown supported.")
    """Display the caption input as a Textarea"""

    alternative_text = CharField(widget=Textarea, required=False)
    """Display the caption input as a Textarea"""

    class Meta:
        model = Photo
        fields = [
            'content_md',
            'in_reply_to',
            'author',
            'tags',
            'published',
        ]

# Admin specs for the Photo model
class PhotoAdmin(SyndicatableAdmin):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = PhotoModelForm
    """Override the dynamically created form with customizations."""

    inlines = [ImagesInline]

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('content_md','in_reply_to','author','tags')
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

# Register your models here.
#admin.site.register(Photo, PhotoAdmin)