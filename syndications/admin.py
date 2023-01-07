from django.contrib import admin, messages
from tweepy.errors import TweepyException
from .models import Syndication, TwitterUser, MastodonStatus, MastodonSyndicatable
from django.utils import timezone
import datetime

# Register your models here.
class SyndicatableAdmin(admin.ModelAdmin):
    readonly_fields = ('syndicated_to_twitter', 'syndicated_to_mastodon')

    def _syndicate_to_twitter(self, request, obj):
        if obj.is_syndicated_to_twitter():
            return obj

        if not obj.is_published:
            self.message_user(request, "Cannot syndicate an unpublished post.", messages.WARNING)
            return obj
   
        try:
            media = obj.get_twitter_media()
            update = obj.to_twitter_status_update()
            response = Syndication.syndicate_to_twitter(update, media)
        except TweepyException as e:
            obj.syndicate_to_twitter = False
            self.message_user(request, f"Error syndicating to Twitter: { str(e) }", messages.WARNING)
            return obj

        try:            
            user = TwitterUser(id_str=response.user.id_str, name=response.user.name, screen_name=response.user.screen_name)
            user.save()

            in_reply_to_status_id_str = response.in_reply_to_status_id_str
            in_reply_to_screen_name = response.in_reply_to_screen_name

            obj.tweet.create(
                id_str=response.id_str, 
                created_at=response.created_at, 
                user=user, 
                full_text=response.text,
                in_reply_to_status_id_str=in_reply_to_status_id_str,
                in_reply_to_screen_name=in_reply_to_screen_name)
            obj.syndicated_to_twitter = timezone.now()
        except Exception as e:
            self._desyndicate_from_twitter(response.id_str, obj)
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }", messages.WARNING)
        
        return obj

    def _desyndicate_from_twitter(self, request, obj):
        if not obj.is_syndicated_to_twitter():
            return obj

        try:
            response = Syndication.delete_from_twitter(obj.tweet.get().id_str)
        except TweepyException as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }", messages.WARNING)
            return obj
        except Exception as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }", messages.WARNING)

        try:
            ts = obj.tweet.get()
            ts.delete()
        except Exception as e:
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }", messages.WARNING)
        
        obj.syndicated_to_twitter = None
        return obj

    def _syndicate_to_mastodon(self, request, obj):
        if obj.is_syndicated_to_mastodon():
            return obj

        if not obj.is_published:
            self.message_user(request, "Cannot syndicate an unpublished post.", messages.WARNING)
            return obj

        try:
            media = obj.get_mastodon_media_upload()
            status = obj.get_mastodon_status_update()
            response = Syndication.syndicate_to_mastodon(status, media)
        except Exception as e:
            obj.syndicate_to_mastodon = False
            self._desyndicate_from_mastodon(None, obj)
            self.message_user(request, f"Error syndicating to Mastodon: { str(e) }", messages.ERROR)
            return obj

        try:
            obj.mastodon_status.create(
                id_str=response['id'], 
                url=response['url'],
                created_at=response['created_at']
            )
            obj.syndicated_to_mastodon = timezone.now()
        except Exception as e:
            self._desyndicate_from_mastodon(response.id, obj)
            self.message_user(request, f"Error updating Mastodon syndication info: { str(e) }", messages.ERROR)
        
        return obj

    def _desyndicate_from_mastodon(self, request, obj):
        if not obj.is_syndicated_to_mastodon():
            return obj

        try:
            response = Syndication.delete_from_mastodon(obj.mastodon_status.get().id_str)
        except Exception as e:
            self.message_user(request, f"Error desyndicating to Mastodon: { str(e) }", messages.ERROR)

        try:
            ms = obj.mastodon_status.get()
            ms.delete()
        except Exception as e:
            self.message_user(request, f"Error updating Mastodon syndication info: { str(e) }", messages.ERROR)
        
        obj.syndicated_to_mastodon = None
        return obj

    def _handle_twitter_syndication(self, request, obj):
        if not obj.syndicate_to_twitter:
            return self._desyndicate_from_twitter(request, obj)            

        return self._syndicate_to_twitter(request, obj)

    def _handle_mastodon_syndication(self, request, obj):
        if not obj.syndicate_to_mastodon:
            return self._desyndicate_from_mastodon(request, obj)            

        return self._syndicate_to_mastodon(request, obj)

    def _handle_syndication(self, request, obj):
        obj = self._handle_twitter_syndication(request, obj)
        obj = self._handle_mastodon_syndication(request, obj)

        return obj

    def save_model(self, request, obj, form, change):
        save_response = super().save_model(request, obj, form, change)

        obj = self._handle_syndication(request, obj)
        obj.save()

        return save_response