from syndications.models import MastodonPushSubscription
from syndications.mastodon_client import Client
from django.conf import settings
from django.urls import reverse

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        encrypt_params = Client.push_subscription_generate_keys()
        endpoint = settings.SITE_URL + reverse('syndications:mastodon_listener')
        subscription = Client.push_subscription_set(endpoint=endpoint, encrypt_params=encrypt_params[1])
        
        MastodonPushSubscription.objects.all().delete()

        sub = MastodonPushSubscription.objects.update_or_create(
            singleton=MastodonPushSubscription.pk, defaults={
            "privkey":encrypt_params[0].get("privkey"),
            "auth":encrypt_params[0].get("auth"),
            "foreign_id":subscription.get("id"),
            "endpoint":subscription.get("endpoint"),
            "alerts":subscription.get("alerts"),
            "server_key":subscription.get("server_key"),
            "policy":subscription.get("policy")})
        
        print(sub)

        print(MastodonPushSubscription.objects.count())


        #Client.push_subscription_subscribe(
        #    endpoint="http://127.0.0.1:8000/mastodon/listener",
        #    subscription_keys_p256dh=)

    