from django.contrib import admin
from .models import Post, Category, Tag
from django.utils.html import format_html
from urllib.parse import quote as urlquote
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect
from syndications.models import Syndication

from syndications.admin import SyndicatableAdmin

class PostAdmin(SyndicatableAdmin):
    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = SyndicatableAdmin.readonly_fields + ('published',)
    #exclude = ('is_published',)
    fieldsets = (
        (None, {
            'fields': ('title','slug','summary','content','author')
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

    def _handle_publish(self, obj, form):
        if not obj.is_published:
            obj.published = None
            return obj
        
        if 'is_published' not in form.changed_data:            
            return obj
        
        obj.published = timezone.now()

        return obj

    def save_model(self, request, obj, form, change):
        obj = self._handle_publish(obj, form)

        return super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)