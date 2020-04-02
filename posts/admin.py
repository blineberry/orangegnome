from django.contrib import admin
from .models import Post, Category, Tag, TwitterSyndication
from django.utils import timezone
import datetime
from django.utils.html import format_html
from urllib.parse import quote as urlquote
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.http import HttpResponseRedirect
from syndications.models import Syndication
from twitter import TwitterError

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = ('published','syndicated_to_twitter',)
    #exclude = ('is_published',)

    def _handle_publish(self, obj, form):
        if not obj.is_published:
            obj.published = None
            return obj
        
        if 'is_published' not in form.changed_data:            
            return obj
        
        obj.published = timezone.now()

        return obj

    def _syndicate(self, request, obj):
        if obj.is_syndicated_to_twitter():
            return obj

        if not obj.is_published:
            self.message_user(request, "Cannot syndicate an unpublished post.", messages.WARNING)
            return obj
   
        try:
            response = Syndication.syndicate_to_twitter(f'{obj.summary} {request.build_absolute_uri(obj.get_absolute_url())}')
        except TwitterError as e:
            self.message_user(request, f"Error syndicating to Twitter: { str(e) }")
            return obj

        try:
            created_at = datetime.datetime.strptime(response.created_at, "%a %b %d %H:%M:%S %z %Y")
            obj.twitter_syndication.create(id_str=response.id_str, created_at=created_at, screen_name=response.user.screen_name)
            obj.syndicated_to_twitter = timezone.now()
        except Exception as e:
            self._desyndicate(response.id_str)
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }")
        
        return obj

    def _desyndicate(self, request, obj):
        if not obj.is_syndicated_to_twitter():
            return obj

        try:
            response = Syndication.delete_from_twitter(obj.twitter_syndication.get().id_str)
        except TwitterError as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }")
            return obj

        try:
            ts = obj.twitter_syndication.get()
            ts.delete()
        except Exception as e:
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }")
        
        obj.syndicated_to_twitter = None
        return obj

    def _handle_syndication(self, request, obj):
        if not obj.syndicate_to_twitter:
            return self._desyndicate(request, obj)            

        return self._syndicate(request, obj)

    def save_model(self, request, obj, form, change):
        obj = self._handle_publish(obj, form)

        obj = self._handle_syndication(request, obj)

        return super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)