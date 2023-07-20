from django.core.management.base import BaseCommand, CommandError
import hashlib
import requests
from syndications.models import StravaWebhook
import datetime

class Command(BaseCommand):
    help = "Create a Strava webhook subscription"
    subscription_url = "https://www.strava.com/api/v3/push_subscriptions"

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help="\"create\", \"view\" or \"delete\"")
        parser.add_argument('client_id', type=str, help="The Strava Client ID")
        parser.add_argument('client_secret', type=str, help="The Strava Client Secret")

    def create(self, client_id, client_secret):
        token = hashlib.md5(str(datetime.timezone.now().timestamp()).encode())
        webhook = StravaWebhook(verify_token=token.hexdigest())
        webhook.save()

        print('requestion subscription')
        response = requests.post(self.subscription_url, data={
            "client_id": client_id,
            "client_secret": client_secret,
            "callback_url": "https://orangegnome.com/syndications/strava/webhook",
            "verify_token": webhook.verify_token,
        })

        if response.status_code != 200:
            webhook.delete()
            print(response.text)
            return
            
        print('saving subscription id')
        webhook.subscription_id = response.json()["id"]
        webhook.save()
        print('done')

    def delete(self, client_id, client_secret):
        print('getting webhook subscriptions')
        webhooks = StravaWebhook.objects.all()

        for webhook in webhooks:
            print(f'deleting webhook sub id {webhook.subscription_id}')
            requests.delete(f'{self.subscription_url}/{webhook.id}')
            webhook.delete()

        print('done')

    def view(self, client_id, client_secret):
        response = requests.get(self.subscription_url, data={
            "client_id": client_id,
            "client_secret": client_secret
        })

        print(response.text)

    def handle(self, *args, **options):
        if options["action"] == "create":
            self.create(options["client_id"], options["client_secret"])

        if options["action"] == "delete":
            self.delete(options["client_id"], options["client_secret"])

        if options["action"] == "view":
            self.view(options["client_id"], options["client_secret"])