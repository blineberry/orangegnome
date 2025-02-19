from django.contrib import admin
from django.forms import ModelForm, CharField
from .models import Bookmark
from feed.admin import SyndicatableAdmin
from feed.widgets import PlainTextCountTextarea, PlainTextCountTextInput
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.contrib import messages

# Register your models here.
# Customize the Admin form
class BookmarkModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    title_md = CharField(
        widget=PlainTextCountTextInput(max=Bookmark.title_max),
        required=False)
    #title = CharField(widget=TextInput)

    quote_md = CharField(
        widget=PlainTextCountTextarea(max=Bookmark.quote_max), 
        required=False)
    """Display the quote input as a Textarea"""

    commentary_md = CharField(
        widget=PlainTextCountTextarea(max=Bookmark.commentary_max), 
        required=False)
    """Display the commentary input as a Textarea"""


    # def validate_publishable(self, cleaned_data:dict):
    #     published = cleaned_data.get("published")

    #     if not published:
    #         return
        
    #     title_txt = cleaned_data.get("title_txt", "")
    #     quote_txt = cleaned_data.get("quote_txt", "")
    #     commentary_txt = cleaned_data.get("commentary_txt", "")

    #     limits = (
    #         ("Title", len(title_txt), Bookmark.title_max),
    #         ("Quote", len(quote_txt), Bookmark.quote_max),
    #         ("Commentary", len(commentary_txt), Bookmark.commentary_max),
    #     )

    #     for limit in limits:
    #         if limit[1] > limit[2]:
    #             raise ValidationError("%s plain text count of %s must be less than the limit of %s to publish." % limit)
            
    # def save(self, *args, **kwargs):
    #     return super().save()

    class Meta:
        model = Bookmark
        fields = [
            'url',
            'title_md',
            'in_reply_to', 
            'quote_md',
            'commentary_md',
            'author',
            'tags',
            'syndicate_to_twitter', 
            'syndicated_to_twitter',
            'published'
        ]

# Admin specs for the Bookmark model
class BookmarkAdmin(SyndicatableAdmin):
    """
    Specifications for the Bookmark Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = BookmarkModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('syndicated_to_twitter', 'syndicated_to_mastodon')
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('url', 'title_md', 'quote_md', 'commentary_md','in_reply_to','author','tags')
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

    list_display = ['url', 'title_txt']
    """The fields to display on the admin list view."""

    actions = ["render_commonmark"]

    @admin.action(description="Render commonmark")
    def render_commonmark(self, request, queryset):
        for obj in queryset:
            obj.render_commonmark_fields()
            obj.save()

    def save_model(self, request:HttpRequest, obj:Bookmark, form:BookmarkModelForm, change:bool):
        obj.render_commonmark_fields()

        if obj.published and not obj.is_publishable():
            obj.published = None
            messages.add_message(request, messages.WARNING, "Unable to publish.")

        return super().save_model(request,obj,form,change)
        

       

# Register your models here.
admin.site.register(Bookmark, BookmarkAdmin)