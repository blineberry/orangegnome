from django.contrib import admin, messages
from tweepy.errors import TweepyException
from .models import Syndication, TwitterUser, MastodonStatus, MastodonSyndicatable
from django.utils import timezone
from django.conf import settings

# Register your models here.
class SyndicatableAdmin(admin.ModelAdmin):
    readonly_fields = ('syndicated_to_twitter', 'syndicated_to_mastodon')

    def _syndicate_to_twitter(self, request, obj):
        if obj.is_syndicated_to_twitter():
            return obj

        if not obj.is_published():
            self.message_user(request, "Cannot syndicate an unpublished post.", messages.WARNING)
            return obj
   
        try:
            media = obj.get_twitter_media()
            update = obj.to_twitter_status_update()
            response = Syndication.syndicate_to_twitter(update, media)
        except Exception as e:
            obj.syndicate_to_twitter = False
            self.message_user(request, f"Error syndicating to Twitter: { str(e) }", messages.ERROR)
            return obj

        try:            
            user = TwitterUser(id_str=settings.TWITTER_ID_STR, name=settings.TWITTER_NAME, screen_name=settings.TWITTER_SCREEN_NAME)
            user.save()

            in_reply_to_status_id_str = update.in_reply_to_status_id
            #in_reply_to_screen_name = response.in_reply_to_screen_name

            obj.tweet.create(
                id_str=response.data["id"], 
                #created_at=response.created_at, 
                user=user, 
                full_text=response.data["text"],
                in_reply_to_status_id_str=in_reply_to_status_id_str,
                #in_reply_to_screen_name=in_reply_to_screen_name
                )
            obj.syndicated_to_twitter = timezone.now()
        except Exception as e:
            self._desyndicate_from_twitter(response.data["id"], obj)
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }", messages.ERROR)
        
        return obj

    def _desyndicate_from_twitter(self, request, obj):
        if not obj.is_syndicated_to_twitter():
            return obj

        try:
            response = Syndication.delete_from_twitter(obj.tweet.get().id_str)
        except TweepyException as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }", messages.ERROR)
            return obj
        except Exception as e:
            self.message_user(request, f"Error desyndicating to Twitter: { str(e) }", messages.ERROR)

        try:
            ts = obj.tweet.get()
            ts.delete()
        except Exception as e:
            self.message_user(request, f"Error updating Twitter syndication info: { str(e) }", messages.ERROR)
        
        obj.syndicated_to_twitter = None
        return obj

    def _syndicate_to_mastodon(self, request, obj):
        if obj.is_syndicated_to_mastodon():
            return obj

        if not obj.is_published():
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
            self._desyndicate_from_mastodon(response.data.id, obj)
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