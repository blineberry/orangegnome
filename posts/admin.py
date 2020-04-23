from django.contrib import admin
from .models import Post, Category
from syndications.admin import SyndicatableAdmin
from notes.admin import PublishableAdmin
from webmentions.models import Webmention

class PostAdmin(SyndicatableAdmin, PublishableAdmin):
    prepopulated_fields = { 'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        content_links = Webmention.get_links_from(obj.content)

        if change:
            old_obj = Post.objects.get(id=obj.id)
            old_links = Webmention.get_links_from(old_obj.content)
            content_links = set(content_links + old_links)

        if (obj.is_published):
            for link in content_links:
                Webmention.send(obj.get_permalink(), link)

        return super().save_model(request, obj, form, change)
    
    #fieldsets = (
    #    (None, {
    #        'fields': ('title','slug','short_content','long_content','author')
    #    }),
    #    ('Metadata', {
    #        'fields': ('category','tags')
    #    }),
    #    ('Syndication', {
    #        'fields': ('syndicate_to_twitter', 'syndicated_to_twitter')
    #    }),
    #    ('Publishing', {
    #        'fields': ('is_published','published')
    #    })
    #)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)