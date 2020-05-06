from django.core.management.base import BaseCommand, CommandError
from syndications.strava_client import Client
from syndications.models import StravaActivity
from exercises.models import Exercise
from profiles.models import Profile

class Command(BaseCommand):
    help = "Imports activities from Strava"
    authorize_uri = "https://www.strava.com/oauth/authorize"
    token_uri = "https://www.strava.com/oauth/token"

    def add_arguments(self, parser):
        parser.add_argument('client_id', type=str, help="The Strava Client ID")
        parser.add_argument('client_secret', type=str, help="The Strava Client Secret")
        parser.add_argument('redirect_uri', type=str, help="The Strava Client Redirect URI")
        parser.add_argument('athlete', type=int, help="Profile Id for the athlete")

    def handle(self, *args, **options):
        athlete = Profile.objects.get(pk=options['athlete'])
        
        client = Client(client_id=options['client_id'], client_secret=options['client_secret'], redirect_uri=options['redirect_uri'])
        authorize_url = client.get_authorize_url()
        
        print("Copy {0} into the browser".format(authorize_url))
        authorize_response = input("Enter the resulting url: ")

        if not client.try_get_tokens(authorize_response):
            print("Required scopes not granted. Please authorize again.")
            print("Copy {0} into the browser".format(authorize_url))
            authorize_response = input("Enter the resulting url: ")

        activities = client.get_activities(per_page=100)

        for activity in activities:
            strava_activity = StravaActivity.objects.create(
                strava_id=activity['id'],
                athlete=activity['athlete']['id'],
                distance=activity['distance'],
                moving_time=activity['moving_time'],
                elapsed_time=activity['elapsed_time'],
                total_elevation_gain=activity['total_elevation_gain'],
                type=activity['type'],
                start_date=activity['start_date'],
                start_date_local=activity['start_date_local'],
                timezone=activity['timezone'],
                private=activity['private'],
            )

            Exercise.objects.create(
                athlete=athlete,
                type=strava_activity.type,
                distance=strava_activity.distance,
                moving_time=strava_activity.moving_time,
                total_elevation_gain=strava_activity.total_elevation_gain,
                start_date=strava_activity.start_date,
                start_date_local=strava_activity.start_date_local,
                timezone=strava_activity.timezone,
                strava_activity=strava_activity,
                is_published=not strava_activity.private,
                published=strava_activity.start_date,
                author=athlete,
                updated=strava_activity.start_date,
            )

        print(len(activities))
        