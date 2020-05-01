from django.contrib import admin
from .models import Note
from syndications.admin import SyndicatableAdmin
from feed.admin import PublishableAdmin
from webmentions.admin import WebmentionAdmin
from webmentions.models import Webmention

# Register your models here.
class NoteAdmin(PublishableAdmin, SyndicatableAdmin, WebmentionAdmin):
    readonly_fields = ('published','syndicated_to_twitter')

    fieldsets = (
        (None, {
            'fields': ('content','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter')
        }),
        ('Publishing', {
            'fields': ('is_published','published')
        })
    )

    filter_horizontal = ('tags',)

    def get_links_to_webmention(self, request, obj, form, change):
        content_links = Webmention.get_links_from_text(obj.content)

        if change:
            old_obj = Note.objects.get(id=obj.id)
            old_links = Webmention.get_links_from_text(old_obj.content)
            content_links = list(set(content_links + old_links))

        if obj.in_reply_to is not None:
            content_links.append(obj.in_reply_to)

        return content_links

    def should_send_webmentions(self, request, obj, form, change):
        return obj.is_published

admin.site.register(Note, NoteAdmin)