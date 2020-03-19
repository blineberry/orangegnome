from django.shortcuts import render
from .models import Profile

# Create your views here.
def home(request):
    return render(request, 'pages/home.html')