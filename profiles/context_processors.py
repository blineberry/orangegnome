from .models import Profile

def owner(request):
    owner = Profile.objects.get_owner()   

    return { 'site_owner': owner }