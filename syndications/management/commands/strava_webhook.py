from django.core.management.base import BaseCommand, CommandError
import hashlib
import requests
from syndications.models import StravaWebhook
import datetime

class Command(BaseCommand):
    help = "Create a Strava webhook subscription"
    subscription_url = "https://www.strava.com/api/v3/push_subscriptions"

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help="\"create\" or \"delete\"")
        parser.add_argument('client_id', type=str, help="The Strava Client ID")
        parser.add_argument('client_secret', type=str, help="The Strava Client Secret")

    def create(self, client_id, client_secret):
        token = hashlib.md5(str(datetime.datetime.now().timestamp()).encode())
        webhook = StravaWebhook(verify_token=token.hexdigest())
        #webhook.save()

        response = requests.post(self.subscription_url, data={
            "client_id": client_id,
            "client_secret": client_secret,
            "callback_url": "https://orangegnome.com/syndications/strava/webhook",
            "verify_token": webhook.verify_token,
        })

        if response.status_code != 200
            print(response.text)

        webhook.subscription_id = response.json()["id"]

    def handle(self, *args, **options):
        self.create(options["client_id"], options["client_secret"])