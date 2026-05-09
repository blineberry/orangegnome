from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from indieauth.forms import AuthForm
from indieauth.models import AuthRequest
from indieauth.services import get_client_metadata
from indieauth.viewmodels import AuthRequestVM
from orangegnome import settings



# Create your views here.
class MetadataView(View):
    def get(self, request, *args, **kwargs):
        metadata = dict()
        metadata['issuer'] = settings.INDIEAUTH_ISSUER
        metadata['authorization_endpoint'] =  settings.SITE_URL + reverse('indieauth:auth')
        metadata['token_endpoint'] =  settings.SITE_URL + reverse('indieauth:token')
        metadata['introspection_endpoint'] =  settings.SITE_URL + reverse('indieauth:introspect')
        metadata['scopes_supported'] =  ['profile']
        metadata['code_challenge_methods_supported'] = AuthRequest.CODE_CHALLENGE_METHODS_SUPPORTED

        return JsonResponse(metadata)

@method_decorator(staff_member_required, name='dispatch')    
class AuthView(View):
    template_name = "indieauth/auth.html"
    form_class = AuthForm

    def get(self, request:HttpRequest, *args, **kwargs)->HttpResponse:
        authRequest = AuthRequest(request.GET)
        client = get_client_metadata(authRequest.client_id)

        if not authRequest.is_redirect_uri_valid(client):
            return HttpResponseBadRequest("invalid redirect_uri")
        
        vm = AuthRequestVM(authRequest, client)
        print(vm.client_name)
        return render(request, self.template_name, { "model" : vm })

class TokenView(View):
    pass

class IntrospectView(View):
    pass