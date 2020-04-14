from django.contrib import admin
from twitter import TwitterError
from .models import Syndication
from django.utils import timezone
import datetime

# Register your models here.
class SyndicatableAdmin(admin.ModelAdmin):
    readonly_fields = ('syndicated_to_twitter',)

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
            obj.tweet.create(id_str=response.id_str, created_at=created_at, screen_name=response.user.screen_name)
            obj.syndicated_to_twitter = timezone.now()
        except Exception as e:
            self._desyndicate(response.id_str, obj)
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }")
        
        return obj

    def _desyndicate(self, request, obj):
        if not obj.is_syndicated_to_twitter():
            return obj

        try:
            response = Syndication.delete_from_twitter(obj.tweet.get().id_str)
        except TwitterError as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }")
            return obj

        try:
            ts = obj.tweet.get()
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
        obj = self._handle_syndication(request, obj)

        return super().save_model(request, obj, form, change)