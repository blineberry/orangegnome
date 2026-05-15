from django.http import HttpRequest, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from indieauth.models import AccessToken, RefreshToken

# Create your views here.
@method_decorator(csrf_exempt, "dispatch")
class RevokeView(View):
    def post(self, request:HttpRequest, *args, **kwargs):
        requested_token = request.POST.get("token")
        
        AccessToken.objects.filter(token=requested_token).delete()
        RefreshToken.objects.filter(token=requested_token).delete()

        return HttpResponse(status=200)
    
