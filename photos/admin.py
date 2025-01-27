from django.contrib import admin
from .models import Photo
from feed.admin import SyndicatableAdmin
from django.forms import ModelForm, CharField, Textarea

# Customize the Admin form
class PhotoModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    caption = CharField(widget=Textarea, help_text="Markdown supported.")
    """Display the caption input as a Textarea"""

    alternative_text = CharField(widget=Textarea)
    """Display the caption input as a Textarea"""

    class Meta:
        model = Photo
        fields = [
            'image',
            'caption',
            'alternative_text',
            'in_reply_to',
            'author',
            'tags',
            'syndicate_to_twitter', 
            'syndicated_to_twitter',
            'published'
        ]

# Admin specs for the Photo model
class PhotoAdmin(SyndicatableAdmin):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = PhotoModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('image_tag','syndicated_to_twitter', 'syndicated_to_mastodon')
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('image_tag', 'image', 'caption', 'alternative_text','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter', 'syndicate_to_mastodon','syndicated_to_mastodon')
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

    list_display = ['image_tag', 'caption']    

# Register your models here.
admin.site.register(Photo, PhotoAdmin)