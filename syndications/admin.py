from django.contrib import admin, messages
from .models import SyndicationAbstract, MastodonStatus, MastodonSyndicatable, MastodonStatusesToProcess, MastodonPush
from django.utils import timezone
from django.conf import settings

# Register your models here.
class SyndicatableAdmin(admin.ModelAdmin):
    readonly_fields = ('syndicated_to_mastodon',)    
    def __syndicate_mastodon_favorite(self, request, obj):
        id = obj.get_status_id_from_url()

        if not id:
            self.message_user(request, f"URL is not a mastodon status")
            return
        
        try: 
            response = SyndicationAbstract.favorite_on_mastodon(id)

            s = obj.syndications.create(
                name=MastodonStatus.instance_name, 
                url=response['url'])
            
            obj.mastodon_status.create(
                id_str=response['id'],
                url=response['url'],
                created_at=response['created_at'],
                syndication=s
            )
            obj.syndicated_to_mastodon = timezone.now()
        except Exception as e:
            self.message_user(request, "Unable to favorite mastodon status: " + str(e), messages.ERROR)
        
        return obj
    
    def __syndicate_mastodon_boost(self, request, obj):
        id = obj.get_status_id_from_url()

        if not id:
            self.message_user(request, f"URL is not a mastodon status")
            return
        
        try: 
            response = SyndicationAbstract.boost_on_mastodon(id)

            s = obj.syndications.create(
                name=MastodonStatus.instance_name, 
                url=response['url'])
            
            obj.mastodon_status.create(
                id_str=response['id'],
                url=response['url'],
                created_at=response['created_at'],
                syndication=s
            )

            obj.syndicated_to_mastodon = timezone.now()
        except Exception as e:
            self.message_user(request, "Unable to boost mastodon status: " + str(e), messages.ERROR)
        
        return obj
    
    def __desyndicate_mastodon_favorite(self, request, obj):
        id = obj.get_status_id_from_url()

        if not id:
            self.message_user(request, f"URL is not a mastodon status")
            return
        
        try: 
            response = SyndicationAbstract.unfavorite_on_mastodon(id)

            s = obj.syndications.filter(name=MastodonStatus.instance_name).delete()
        except Exception as e:
            self.message_user(request, "Unable to favorite mastodon status: " + str(e), messages.ERROR)
        
        return obj
    
    def __desyndicate_mastodon_boost(self, request, obj):
        id = obj.get_status_id_from_url()

        if not id:
            self.message_user(request, f"URL is not a mastodon status")
            return
        
        try: 
            response = SyndicationAbstract.unboost_on_mastodon(id)

            s = obj.syndications.filter(name=MastodonStatus.instance_name).delete()
        except Exception as e:
            self.message_user(request, "Unable to favorite mastodon status: " + str(e), messages.ERROR)
        
        return obj

    def _syndicate_to_mastodon(self, request, obj):
        if obj.is_syndicated_to_mastodon():
            return obj

        if not obj.is_published():
            self.message_user(request, "Cannot syndicate an unpublished post.", messages.WARNING)
            return obj
        
        if obj.is_mastodon_favorite():
            return self.__syndicate_mastodon_favorite(request,obj)
        
        if obj.is_mastodon_boost():
            return self.__syndicate_mastodon_boost(request,obj)

        try:
            media = obj.get_mastodon_media_upload()
            status = obj.get_mastodon_status_update()
            response = SyndicationAbstract.syndicate_to_mastodon(status, media)
        except Exception as e:
            obj.syndicate_to_mastodon = False
            self._desyndicate_from_mastodon(None, obj)
            self.message_user(request, f"Error syndicating to Mastodon: { str(e) }", messages.ERROR)
            return obj

        try:
            syndication = obj.syndications.create(
                name=MastodonStatus.instance_name,
                url=response['url'])
            
            obj.mastodon_status.create(
                id_str=response['id'], 
                url=response['url'],
                created_at=response['created_at'],
                syndication=syndication
            )
            
            obj.syndicated_to_mastodon = timezone.now()
        except Exception as e:
            self._desyndicate_from_mastodon(response["id"], obj)
            self.message_user(request, f"Error updating Mastodon syndication info: { str(e) }", messages.ERROR)
        
        return obj

    def _desyndicate_from_mastodon(self, request, obj):
        if not obj.is_syndicated_to_mastodon():
            return obj        

        if obj.is_mastodon_favorite():
            return self.__desyndicate_mastodon_favorite(request,obj)
        
        if obj.is_mastodon_boost():
            return self.__desyndicate_mastodon_boost(request, obj)

        try:
            response = SyndicationAbstract.delete_from_mastodon(obj.mastodon_status.get().id_str)
        except Exception as e:
            self.message_user(request, f"Error desyndicating to Mastodon: { str(e) }", messages.ERROR)

        try:
            s = obj.syndications.filter(name=MastodonStatus.instance_name).delete()
        except Exception as e:
            self.message_user(request, f"Error updating Mastodon syndication info: { str(e) }", messages.ERROR)
        
        obj.syndicated_to_mastodon = None
        return obj

    def _handle_mastodon_syndication(self, request, obj):
        if not obj.syndicate_to_mastodon:
            return self._desyndicate_from_mastodon(request, obj)            

        return self._syndicate_to_mastodon(request, obj)

    def _handle_syndication(self, request, obj):
        obj = self._handle_mastodon_syndication(request, obj)

        return obj

    def save_model(self, request, obj, form, change):
        save_response = super().save_model(request, obj, form, change)

        obj = self._handle_syndication(request, obj)
        obj.save()

        return save_response
    
admin.site.register(MastodonStatusesToProcess)
admin.site.register(MastodonStatus)
admin.site.register(MastodonPush)