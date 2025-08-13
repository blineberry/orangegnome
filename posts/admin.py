from django.contrib import admin

from feed.widgets import PlainTextCountTextInput, PlainTextCountTextarea
from .models import Post, Category
from notes.admin import SyndicatableAdmin
from django.forms import ModelForm, CharField, Textarea

class PostModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    
    summary_md = CharField(widget=PlainTextCountTextarea(max=Post.summary_max), help_text="Markdown supported.", required=False)
    title_md = CharField(widget=PlainTextCountTextInput(max=Post.title_max), help_text="Markdown supported.")
    content_md = CharField(widget=PlainTextCountTextarea(), help_text="Markdown supported.", required=False)
    
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
            'category',
            'tags',
        ]

class PostAdmin(SyndicatableAdmin):
    form = PostModelForm

    prepopulated_fields = { 'slug': ('title_md',)}
    readonly_fields = ('syndicated_to_mastodon',)
    
    fieldsets = (
        (None, {
            'fields': ('title_md','slug','summary_md','in_reply_to','content_md','author')
        }),
        ('Metadata', {
            'fields': ('category','tags')
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
admin.site.register(Post, PostAdmin)
admin.site.register(Category)