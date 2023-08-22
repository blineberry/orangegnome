from django.contrib import admin
from django.forms import ModelForm
from .models import Repost
from syndications.admin import SyndicatableAdmin
from feed.admin import PublishableAdmin

# Register your models here.
# Customize the Admin form
class RepostModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    class Meta:
        model = Repost
        fields = [
            'url',
            'content',
            'source_author_name',
            'source_author_url',
            'author',
            'tags',
            'syndicate_to_mastodon', 
            'syndicated_to_mastodon',
            'published'
        ]

# Admin specs for the Repost model
class RepostAdmin(PublishableAdmin, SyndicatableAdmin):
    """
    Specifications for the Repost Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin
    """

    form = RepostModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('url', 'source_name', 'content', 'source_author_name', 'source_author_url', 'author', 'tags')
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

    list_display = ['url', 'source_author_name']
    """The fields to display on the admin list view."""

# Register your models here.
admin.site.register(Repost, RepostAdmin)