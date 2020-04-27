from django.contrib import admin
from .models import Post, Category
from syndications.admin import SyndicatableAdmin
from notes.admin import PublishableAdmin
from webmentions.models import Webmention
from webmentions.admin import WebmentionAdmin

class PostAdmin(SyndicatableAdmin, PublishableAdmin, WebmentionAdmin):
    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = ('published','syndicated_to_twitter')
    
    fieldsets = (
        (None, {
            'fields': ('title','slug','summary','content','author')
        }),
        ('Metadata', {
            'fields': ('category','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter')
        }),
        ('Publishing', {
            'fields': ('is_published','published')
        })
    )
    
    def get_links_to_webmention(self, request, obj, form, change):
        content_links = Webmention.get_links_from_html(obj.content)

        if change:
            old_obj = Post.objects.get(id=obj.id)
            old_links = Webmention.get_links_from_html(old_obj.content)
            content_links = set(content_links + old_links)

        return list(content_links)

    def should_send_webmentions(self, request, obj, form, change):
        return obj.is_published

    def save_model(self, request, obj, form, change):
        print("Post save")
        
        return super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)