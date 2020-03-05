from django.shortcuts import render
from .models import Person

# Create your views here.
def home(request):
    owner = Person()

    if Person.objects.all()[:1].exists():
        owner = Person.objects.all()[0]
        print(owner.url)

    return render(request, 'pages/home.html', { 'owner': owner })