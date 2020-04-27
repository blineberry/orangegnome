from django.contrib import admin
from tweepy import TweepError
from .models import Syndication, TwitterUser
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
            response = Syndication.syndicate_to_twitter(obj.to_twitter_status())
        except TweepError as e:
            self.message_user(request, f"Error syndicating to Twitter: { str(e) }")
            return obj

        try:            
            user = TwitterUser(id_str=response.user.id_str, name=response.user.name, screen_name=response.user.screen_name)
            user.save()

            full_text = response.full_text

            obj.tweet.create(id_str=response.id_str, created_at=response.created_at, user=user, full_text=full_text)
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
        except TweepError as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }")
            return obj
        except Exception as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }")

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
        print('Syndication save')
        obj = self._handle_syndication(request, obj)

        return super().save_model(request, obj, form, change)