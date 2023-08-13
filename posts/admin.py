from django.contrib import admin
from .models import Post, Category
from syndications.admin import SyndicatableAdmin
from notes.admin import PublishableAdmin
from django.forms import ModelForm, CharField, Textarea

class PostModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """
    
    summary = CharField(widget=Textarea, help_text="Markdown supported.")
    """Display the summary input as a Textarea."""

    class Meta:
        model = Post
        fields = [
            'published',
            'syndicate_to_twitter',
            'syndicated_to_twitter',
            'syndicate_to_mastodon',
            'syndicated_to_mastodon',
            'title',
            'slug',
            'summary',
            'in_reply_to', 
            'content',
            'author',
            'category',
            'tags',
        ]

class PostAdmin(SyndicatableAdmin, PublishableAdmin):
    form = PostModelForm

    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = ('syndicated_to_twitter', 'syndicated_to_mastodon')
    
    fieldsets = (
        (None, {
            'fields': ('title','slug','summary','in_reply_to','content','author')
        }),
        ('Metadata', {
            'fields': ('category','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter', 'syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )

    filter_horizontal = ('tags',)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)