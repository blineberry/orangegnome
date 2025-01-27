from django.contrib import admin
from .models import Note
from syndications.admin import SyndicatableAdmin
from feed.admin import PublishableAdmin, SyndicationInline
from django.forms import ModelForm, CharField, Textarea
from base.widgets import PlainTextCountTextarea

# Customize the Admin form
class NoteModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    content = CharField(widget=PlainTextCountTextarea(max=Note.plain_text_limit), help_text="Markdown supported.")
    """Display the content input as a Textarea"""

    class Meta:
        model = Note
        fields = [
            'content',
            'in_reply_to',
            'author',
            'tags',
            'syndicate_to_twitter',
            'syndicated_to_twitter',
            'published'
        ]

# Admin specs for the Note model
class NoteAdmin(PublishableAdmin, SyndicatableAdmin):
    """
    Specifications for the Note Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = NoteModelForm
    """Override the dynamically created form with customizations."""


    inlines = [SyndicationInline]

    readonly_fields = ('syndicated_to_twitter', 'syndicated_to_mastodon')
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('content','in_reply_to','author','tags')
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

admin.site.register(Note, NoteAdmin)