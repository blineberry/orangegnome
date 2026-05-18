from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q



from indieauth.models import AccessToken, RefreshToken, TokenBase

# Create your views here.
@method_decorator(csrf_exempt, name="dispatch")
class IntrospectView(View):    
    def get_bearer(self, request:HttpRequest)->bool:
        is_bearer = False
        token = None

        auth_header = request.headers.get("Authorization")

        if auth_header is None:
            return None

        parts = auth_header.split(" ")

        for p in parts:
            if p.strip() == "":
                continue
            if p.lower() == "bearer":
                is_bearer = True
                
                if token is not None:
                    return token
                
                continue
            
            token = p

            if is_bearer:
                return token
            
        return token

    def get_token(self, request:HttpRequest)->TokenBase:
        token = request.POST.get("token")
        access = AccessToken.objects.filter(Q(token=token),Q(expires_utc__gte=timezone.now()) | Q(expires_utc=None)).first()
        refresh = RefreshToken.objects.filter(Q(token=token),Q(expires_utc__gte=timezone.now()) | Q(expires_utc=None)).first()

        if request.POST.get("token_hint") == "refresh_token" and refresh is not None:
            return refresh
        
        if access is not None:
            return access
        
        return refresh

    def post(self, request:HttpRequest, *args, **kwargs)->HttpResponse:    
        # based off of previous version (https://indieauth.spec.indieweb.org/20201126/#access-token-verification-request)
        # I think authorization is supposed to be the same token in the bearer 
        # auth as in the request body

        bearer = self.get_bearer(request)

        if bearer is None:
            return HttpResponse(status=401)
                
        if bearer != request.POST.get("token"):
            return HttpResponse(status=403)

        token = self.get_token(request)

        if (token is None or 
            token.is_expired()):
            return JsonResponse({ "active": False })
        
        return JsonResponse(token.to_verification_response())

