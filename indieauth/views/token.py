from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse, QueryDict
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from indieauth.models import AccessToken, AuthCode, RefreshToken

def validate_request(values:QueryDict, auth:AuthCode)->tuple[bool,str]:
    if auth is None:
        return (False, "invalid code")
    
    if auth.is_expired():
        return (False, "invalid code")
    
    if values.get("client_id") is None or values.get("client_id") != auth.client_id:
        return (False, "invalid client_id")
    
    if values.get("redirect_uri") is None or values.get("redirect_uri") != auth.redirect_uri:
        return (False, "invalid redirect_uri")
    
    if values.get("code_verifier") is None or not auth.verify_challenge_code(values.get("code_verifier")):
        return (False, "invalid code_verifier")
    
    return (True, "")

# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
class TokenView(View):
    def post(self, request:HttpRequest, *args, **kwargs):
        if request.POST.get("grant_type", "") == "refresh_token":
            return self.refresh_token_response(request, *args, **kwargs)
        
        return self.access_token_response(request, *args, **kwargs)
    
    def access_token_response(self, request:HttpRequest, *args, **kwargs):
        auth = AuthCode.objects.filter(code = request.POST.get("code")).first()
        AuthCode.objects.filter(code = request.POST.get("code")).delete()

        success, err_msg = validate_request(request.POST, auth)
        
        if not success:
            return HttpResponseBadRequest(err_msg)
        
        if auth.scope is None or auth.scope.strip() == "":
            return HttpResponseBadRequest("authorized scopes are required")
        
        access = AccessToken.from_auth_code(auth)
        refresh = RefreshToken.from_auth_code(auth)
        access.save()
        refresh.save()

        return JsonResponse(access.to_token_response(refresh_token=refresh.token))
    
    def refresh_token_response(self, request:HttpRequest, *args, **kwargs):
        if request.POST.get("grant_type") != "refresh_token":
            return HttpResponseBadRequest("{\"error\": \"invalid grant_type\"}")
        
        token = RefreshToken.objects.filter(token=request.POST.get("refresh_token"),expires_utc__gte=timezone.now()).first()
        RefreshToken.objects.filter(token=request.POST.get("refresh_token")).delete()

        if token is None or token.client_id != request.POST.get("client_id"):
            return HttpResponseBadRequest("{\"error\": \"invalid token\"}")
        
        scope = token.update_scope(request.POST.get("scope"))

        access = AccessToken.from_refresh_token(token,scope)
        refresh = RefreshToken.from_refresh_token(token,scope)
        access.save()
        refresh.save()

        return JsonResponse(access.to_token_response(refresh_token=refresh.token))
