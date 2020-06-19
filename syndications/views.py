from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

# Create your views here.
class StravaWebhookView(View):
    def get(self, request, *args, **kwargs):
        print(request)

        if 'hub.mode' not in request.GET:
            return HttpResponseBadRequest()

        if 'hub.challenge' not in request.GET:
            return HttpResponseBadRequest()

        if 'hub.verify_token' not in request.GET:
            return HttpResponseBadRequest()
        
        if request.GET['hub.mode'] != "subscribe":
            return HttpResponseBadRequest()

        return JsonResponse({'hub.challenge':request.GET['hub.challenge']})

    def post(self):
        pass
