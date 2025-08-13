from django.contrib import admin
from .models import Note
from feed.admin import SyndicatableAdmin
from django.forms import ModelForm, CharField, Textarea
from feed.widgets import PlainTextCountTextarea

# Customize the Admin form
class NoteModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    content_md = CharField(widget=PlainTextCountTextarea(max=Note.content_max), help_text="Markdown supported.")
    """Display the content input as a Textarea"""

    class Meta:
        model = Note
        fields = [
            'content_md',
            'in_reply_to',
            'author',
            'tags',
            'published'
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

admin.site.register(Note, NoteAdmin)