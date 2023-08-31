import json
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import StravaWebhook, StravaActivity, StravaWebhookEvent, Reply, Repost, Like, MastodonPush, MastodonPushSubscription
from exercises.models import Exercise
from profiles.models import Profile
from django.views.generic.detail import DetailView
from .mastodon_client import Client

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class StravaWebhookView(View):
    def get(self, request, *args, **kwargs):
        if 'hub.mode' not in request.GET:
            return HttpResponseBadRequest()

        if 'hub.challenge' not in request.GET:
            return HttpResponseBadRequest()

        if 'hub.verify_token' not in request.GET:
            return HttpResponseBadRequest()
        
        if request.GET['hub.mode'] != "subscribe":
            return HttpResponseBadRequest()

        webhook = StravaWebhook.objects.all()[0]

        if request.GET['hub.verify_token'] != webhook.verify_token:
            return HttpResponseBadRequest()

        return JsonResponse({'hub.challenge':request.GET['hub.challenge']})

    def post(self, request, *args, **kwargs):
        event_json = json.loads(request.body.decode("utf-8"))

        event = StravaWebhookEvent(
            object_type = event_json['object_type'],
            object_id = event_json['object_id'],
            aspect_type = event_json['aspect_type'],
            updates = json.dumps(event_json['updates']),
            owner_id = event_json['owner_id'],
            subscription_id = event_json['subscription_id'],
            event_time = event_json['event_time'],
        )
        event.save()
        return HttpResponse(status=200)


        webhook = StravaWebhook.objects.all()[0]

        if webhook.subscription_id != activity['subscription_id ']:
            return HttpResponse(status=404)

        if activity['object_type'] != "activity":
            return HttpResponse(status=200)

        if activity['aspect_type'] == "delete":
            strava_activity = StravaActivity.objects.filter(strava_id=activity["object_id"])[:1]
            
            if len(strava_activity) == 0:
                return HttpResponse(status=200)

            strava_activity = strava_activity[0]

            strava_activity.content_object.delete()
            strava_activity.delete()
            return HttpResponse(status=200)

        if activity['aspect_type'] == 'create':
            athlete = Profile.objects.filter(is_owner=True)[0]

            exercise = Exercise.objects.create(
                athlete=athlete,
                type=activity['updates']['type'],
                distance=activity['updates']['distance'],
                moving_time=activity['updates']['moving_time'],
                total_elevation_gain=activity['updates']['total_elevation_gain'],
                start_date=activity['updates']['start_date'],
                start_date_local=activity['updates']['start_date_local'],
                timezone=activity['updates']['timezone'],
                is_published=not activity['updates']['private'],
                published=activity['updates']['start_date'],
                author=athlete,
                updated=activity['updates']['start_date'],
            )
            exercise.strava_activity.create(
                strava_id=activity['object_id'],
                athlete=activity['owner_id'],
                distance=activity['updates']['distance'],
                moving_time=activity['updates']['moving_time'],
                elapsed_time=activity['updates']['elapsed_time'],
                total_elevation_gain=activity['updates']['total_elevation_gain'],
                type=activity['updates']['type'],
                start_date=activity['updates']['start_date'],
                start_date_local=activity['updates']['start_date_local'],
                timezone=activity['updates']['timezone'],
                private=activity['updates']['private'],
            )
            return HttpResponse(status=200)

        if activity['aspect_type'] == 'update':
            strava_activity = StravaActivity.objects.filter(strava_id=activity["object_id"])[:1]
            
            if len(strava_activity) == 0:
                return HttpResponse(status=200)

            strava_activity = strava_activity[0]

            if strava_activity is None:
                return HttpResponse(status=200)

            updatable_properties = [
                'distance',
                'moving_time',
                'elapsed_time',
                'total_elevation_gain',
                'type',
                'start_date',
                'start_date_local',
                'timezone',
                'private',
            ]

            strava_activity.athlete = activity['owner_id']

            for prop in updatable_properties:
                if prop not in activity['updates']:
                    continue

                setattr(strava_activity, prop, activity['updates'][prop])

            strava_activity.save()


            exercise = strava_activity.content_object

            for prop in updatable_properties:
                if prop not in activity['updates']:
                    continue

                if prop == 'elapsed_time':
                    continue

                if prop == 'private':
                    exercise.published = not activity['updates'][prop]
                    continue

                if prop == 'start_date':
                    exercise.published = activity['updates'][prop]
                    exercise.updated = activity['updates'][prop]

                setattr(exercise, prop, activity['updates'][prop])

            exercise.save()
            return HttpResponse(status=200)

class ReplyView(DetailView):
    model = Reply

class RepostView(DetailView):
    model = Repost

class LikeView(DetailView):
    model = Like

@method_decorator(csrf_exempt, name='dispatch')
class MastodonListener(View):
    def post(self, request):
        push = MastodonPush()

        try:
            subscription = MastodonPushSubscription.objects.first()
            n = Client.push_subscription_decrypt_push(
                data=request.POST, 
                decrypt_params={
                    "privkey":subscription.privkey,
                    "auth": subscription.auth
                },
                encryption_header=request.META.get('Encryption'),
                crypto_key_header=request.META.get('Crypto-Key')
            )
            push.access_token = n.get("access_token")
            push.body = n.get("body")
            push.icon = n.get("icon")
            push.notification_id = n.get("notification_id")
            push.notification_type = n.get("notification_type")
            push.preferred_local = n.get("preferred_local")
            push.title = n.get("title")
            push.result = "success"
            push.save()
            return HttpResponse(status=200)
        except Exception as e:
            push.result = str(e)# + "\n\n" + json.dumps(request.__dict__,indent=2)
            push.save()
            return HttpResponse(status=200)