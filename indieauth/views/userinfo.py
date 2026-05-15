from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from indieauth.models import AccessToken

# Create your views here.
@method_decorator(csrf_exempt, "dispatch")
class UserInfoView(View):
    def get_bearer_token(self, request:HttpRequest)->str:
        headers = request.headers
        auth_header = headers.get("Authorization")

        if auth_header is None:
            return None
        
        parts = auth_header.split(" ")
        token = None

        for p in parts:
            if p.strip() == "":
                continue
            if p.lower() == "bearer":
                continue

            token = p
            break

        return token
    
    def get(self, request:HttpRequest, *args, **kwargs):
        bearer = self.get_bearer_token(request)

        if bearer is None:
            return HttpResponse("invalid_token", status=401)
        
        token = AccessToken.objects.filter(token=bearer,expires_utc__gte=timezone.now()).first()

        if token is None:
            return HttpResponse("invalid_token", status=401)
        
        if "profile" not in token.get_scopes():
            return HttpResponse("insufficient_scope", status=403)
        
        return JsonResponse(token.to_userinfo_response())
        