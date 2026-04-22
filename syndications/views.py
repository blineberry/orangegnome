import json
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import StravaWebhook, StravaActivity, StravaWebhookEvent, Reply, Repost, Like, MastodonPush, MastodonPushSubscription
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
            result_dict = {
                #"body": request.body,
                "body_is_not_none": request.body is not None,
                "post": request.POST,
                "get": request.GET,
                "encoding": request.encoding,
                "content_type": request.content_type,
                "meta_content_type": request.META.get("CONTENT_TYPE"),
                "meta_content_length": request.META.get("CONTENT_LENGTH"),
                "meta_encryption_header": request.META.get('Encryption'),
                "meta_http_encryption_header": request.META.get('HTTP_ENCRYPTION'),
                "meta_crypto_key_header": request.META.get('Crypto-Key'),
                "meta_http_crypto_key_header": request.META.get('HTTP_CRYPTO_KEY'),
            }

            push.result = json.dumps(result_dict)
            push.save()
            #return HttpResponse(status=200)

            data = request.read(int(request.META.get("CONTENT_LENGTH")))
            encryption = request.META.get('HTTP_ENCRYPTION')
            crypto_key = request.META.get('HTTP_CRYPTO_KEY')
            subscription = MastodonPushSubscription.objects.first()

            n = Client.push_subscription_decrypt_push(
                data=data, 
                decrypt_params={
                    "privkey":int(subscription.privkey),
                    "auth": subscription.auth
                },
                encryption_header=encryption,
                crypto_key_header=crypto_key
            )
            push.access_token = n.get("access_token")
            push.body = n.get("body")
            push.icon = n.get("icon")
            push.notification_id = n.get("notification_id")
            push.notification_type = n.get("notification_type")
            push.preferred_local = n.get("preferred_local")
            push.title = n.get("title")
            push.result = push.result + "\n\nsuccess"
            push.save()
            return HttpResponse(status=200)
        except Exception as e:
            push.result = push.result + "\n\n" + str(e)# + "\n\n" + json.dumps(request.__dict__,indent=2)
            push.save()
            return HttpResponse(status=200)