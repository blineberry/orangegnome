from django.contrib import admin
from .models import Post, Category, Tag
from syndications.admin import SyndicatableAdmin
from notes.admin import PublishableAdmin

class PostAdmin(SyndicatableAdmin, PublishableAdmin):
    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = SyndicatableAdmin.readonly_fields + PublishableAdmin.readonly_fields
    
    fieldsets = (
        (None, {
            'fields': ('title','slug','short_content','long_content','author')
        }),
        ('Metadata', {
            'fields': ('category','tags',)
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter')
        }),
        ('Publishing', {
            'fields': ('is_published','published')
        })
    )

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)