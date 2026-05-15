from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


from indieauth.models import AccessToken, RefreshToken, TokenBase

# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
class IntrospectView(View):    
    def get_token(self, request:HttpRequest)->TokenBase:
        token = request.POST.get("token")
        access = AccessToken.objects.filter(token=token,expires_utc__gte=timezone.now()).first()
        refresh = RefreshToken.objects.filter(token=token,expires_utc__gte=timezone.now()).first()

        if request.POST.get("token_hint") == "refresh_token" and refresh is not None:
            return refresh
        
        if access is not None:
            return access
        
        return refresh

    def post(self, request:HttpRequest, *args, **kwargs)->HttpResponse:
        # spec requires auth on this endpoint. Can't use client_id as a Basic
        # auth username becauseo of colons. Using the token also as the auth
        # seems ineffective. Using client_id in post body seems like least bad
        # option.
        client_id = request.POST.get("client_id")

        if client_id is None:
            return HttpResponse(status=401)
        
        token = self.get_token(request)

        if (token is None or 
            token.client_id != client_id or 
            token.is_expired()):
            return JsonResponse({ "active": False })
        
        return JsonResponse(token.to_verification_response())

