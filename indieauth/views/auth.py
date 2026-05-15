import ipaddress
import re
from urllib.parse import urlsplit

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse, QueryDict
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.middleware.csrf import CsrfViewMiddleware

from indieauth.models import AuthCode, ClientMetadata, ServerMetadata
from indieauth.viewmodels import AuthRequestVM, AuthSubmissionVM
from indieauth.views.token import validate_request

# Create your views here.
class AuthView(View):
    SESSION_REQUEST_KEY = "INDIEAUTH_AUTH_REQUEST"

    template_name = "indieauth/auth.html"

    @staticmethod
    def is_client_id_valid(client_id)->bool:
        # Clients are identified by a [URL].
        if client_id is None:
            return False
        
        split = urlsplit(client_id)
        
        # Client identifier URLs MUST have either an https or http scheme,
        valid_schemes = ['http','https']
        if split.scheme not in valid_schemes:
            return False
        
        # MUST contain a path component,
        if split.path == '':
            return False

        # MUST NOT contain single-dot or double-dot path segments,
        segments = split.path.split(sep="/")
        invalid_segments = [".", ".."]
        for segment in segments:
            if segment in invalid_segments:
                return False
            
        # MAY contain a query string component, 
        # MUST NOT contain a fragment component, 
        if split.fragment != '':
            return False
        
        # MUST NOT contain a username or password component, and 
        if split.username != None:
            return False
        
        if split.password != None:
            return False
        
        # MAY contain a port. Additionally, 
        # host names MUST be domain names or a loopback interface and MUST NOT be IPv4 or IPv6 addresses except for IPv4 127.0.0.1 or IPv6 [::1].        
        valid_ips = ["127.0.0.1", "[::1]"]        
        if split.netloc not in valid_ips:
            # ipv6
            pattern = re.compile(r"^\[[a-zA-Z0-9:]+\](:[0-9]+){0,1}")
            if pattern.match(split.netloc):
                if split.netloc[-1] == "]":
                    return False
                
                ip, sep, port = split.netloc.rpartition(":")
                if ip not in valid_ips:
                    return False
            else:
                host = split.netloc.rsplit(":")[0]
                if host not in valid_ips:
                    try:
                        ipaddress.ip_address(host)
                        return False
                    except:
                        pass                

        return True
    
    @staticmethod
    def is_redirect_uri_valid(redirect_uri:str, client_id:str, client_redirect_uris:list[str])->bool:
        redirect_parts = urlsplit(redirect_uri)
        client_id_parts = urlsplit(client_id)
        
        # If the URL scheme, host or port of the redirect_uri in the request do not match that of the client_id, 
        if (redirect_parts.scheme == client_id_parts.scheme and
            redirect_parts.netloc == client_id_parts.netloc):
            return True

        # then the authorization endpoint SHOULD verify that the requested redirect_uri matches one of the redirect URLs published by the client, and SHOULD block the request from proceeding if not.
        return redirect_uri in client_redirect_uris

    @staticmethod
    def validate_request(values:QueryDict)->tuple[bool,ClientMetadata,str]:
        if values.get("code_challenge") is None:
            return (False, None, "code_challenge required")

        client_id = values.get("client_id")

        if not AuthView.is_client_id_valid(client_id):
            return (False, None, "invalid client_id")
        
        client:ClientMetadata = ClientMetadata.fetch(client_id)
        
        client_redirect_uris = []
        if client is not None and client.redirect_uris is not None:
            client_redirect_uris = client.redirect_uris
        
        if not AuthView.is_redirect_uri_valid(values.get("redirect_uri"), client_id, client_redirect_uris):
            return (False, client, "invalid redirect_uri")
        
        return (True, client, "")

    # Needed for manual csrf check
    @staticmethod
    def get_response(request):
        pass

    def get(self, request:HttpRequest, *args, **kwargs)->HttpResponse:
        if not request.user.is_authenticated:
            return redirect(reverse("admin:login", query={"next":request.path}))
        
        success, client, error_msg = AuthView.validate_request(request.GET)

        if not success:
            return HttpResponseBadRequest(error_msg)    

        vm = AuthRequestVM(request.GET, client)
        
        return render(request, self.template_name, { "model" : vm })
    
    def post(self, request:HttpRequest, *args, **kwargs):
        if request.POST.get("grant_type", "") == "authorization_code":
            return self.profile_url_response(request, *args, **kwargs)
        
        return self.auth_code_response(request, *args, **kwargs)

    def auth_code_response(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("admin:login", query={"next":request.path}))
        
        request.csrf_processing_done = False
        reason = CsrfViewMiddleware(AuthView.get_response).process_view(request, None, (), {})

        if reason:
            return HttpResponse("Invalid CSRF token", status_code=403)

        success, client, error_msg = AuthView.validate_request(request.POST)

        if not success:
            return HttpResponseBadRequest(error_msg)

        vm = AuthSubmissionVM(request.POST, ServerMetadata.issuer)

        if vm.should_generate_auth_code():
            user = request.user
            auth = AuthCode.from_auth_submission_vm(vm, user.id)
            auth.save()

            return redirect(vm.get_redirect_uri(auth.code))
        else:
            return redirect(vm.get_redirect_uri())
        
    def profile_url_response(self, request, *args, **kwargs):
        auth = AuthCode.objects.filter(code = request.POST.get("code")).first()
        AuthCode.objects.filter(code = request.POST.get("code")).delete()

        success, err_msg = validate_request(request.POST, auth)
        
        if not success:
            return HttpResponseBadRequest(err_msg)

        return JsonResponse(auth.to_profile_url_response())

