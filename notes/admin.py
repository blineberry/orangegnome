from django.contrib import admin
from django.utils import timezone
from .models import Note
from syndications.admin import SyndicatableAdmin

# Register your models here.
class PublishableAdmin(admin.ModelAdmin):
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

class NoteAdmin(PublishableAdmin, SyndicatableAdmin):
    pass
    #fieldsets = (
    #    (None, {
    #        'fields': ('short_content','author','tags')
    #    }),
    #    ('Syndication', {
    #        'fields': ('syndicate_to_twitter', 'syndicated_to_twitter')
    #    }),
    #    ('Publishing', {
    #        'fields': ('is_published','published')
    #    })
    #)

admin.site.register(Note, NoteAdmin)