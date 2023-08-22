from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea
from .models import Like
from syndications.admin import SyndicatableAdmin
from feed.admin import PublishableAdmin

# Register your models here.
# Customize the Admin form
class LikeModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    quote = CharField(widget=Textarea, required=False)
    """Display the quote input as a Textarea"""

    commentary = CharField(widget=Textarea, required=False)
    """Display the commentary input as a Textarea"""

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
class LikeAdmin(PublishableAdmin, SyndicatableAdmin):
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
            'fields': ('url', 'author','tags')
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

# Register your models here.
admin.site.register(Like, LikeAdmin)