from django.shortcuts import render
from django.views import View
from .models import PendingIncomingWebmention
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class IncomingWebmentionHandler(View):
    http_method_names = ["get","post"]

    def dispatch(self, request, *args, **kwargs):    
        print(request)

        source = request.POST.get("source")
        target = request.POST.get("target")

        incomingWebmention = PendingIncomingWebmention.objects.get_or_create(source=source, target=target)[0]
        incomingWebmention.tries = 0
        incomingWebmention.result = None
        incomingWebmention.processed = False
        print(incomingWebmention)

        result = incomingWebmention.verify_request_and_save()
        print(result)

        if not result.get('success'):
            return HttpResponse(result.get('validation_error_message'), status=400)

        return HttpResponse(status=202)
