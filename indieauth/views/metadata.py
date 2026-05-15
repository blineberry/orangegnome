from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from indieauth.models import ServerMetadata

# Create your views here.
class MetadataView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(ServerMetadata(reverse).to_json())
