from django.shortcuts import render
from .models import Profile

# Create your views here.
def home(request):
    owner = Profile.objects.get_owner()   

    return render(request, 'pages/home.html', { 'owner': owner })