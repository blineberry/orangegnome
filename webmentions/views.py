from django.shortcuts import render
from django.views import View
from .models import IncomingWebmention
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import generic
from .models import WebmentionList

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class IncomingWebmentionHandler(View):
    http_method_names = ["post"]

    def dispatch(self, request, *args, **kwargs):    

        source = request.POST.get("source")
        target = request.POST.get("target")

        incomingWebmention = IncomingWebmention.objects.get_or_create(source=source, target=target)[0]
        incomingWebmention.reset()
        incomingWebmention.tries = 0
        incomingWebmention.result = ""
        incomingWebmention.processed = False

        result = incomingWebmention.verify_request_and_save()

        if not result.get('success'):
            return HttpResponse(result.get('validation_error_message'), status=400)

        return HttpResponse(status=202)


class WebmentionableMixin(generic.base.ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        webmentions = context["object"].webmentions.filter(approved=True).filter(verified=True)
        context['webmentions'] = WebmentionList(webmentions=webmentions)
        return context