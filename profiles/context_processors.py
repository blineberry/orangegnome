from .models import Profile

def owner(request):
    owner = Profile.objects.get_owner()

    return { 'profiles': 
        {
            'site_owner': owner 
        }
    }