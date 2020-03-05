from django.shortcuts import render

# Create your views here.
def home(request):
    context = {
        'card': {
            'photoUrl': 'https://s.gravatar.com/avatar/3acbb5f9e3196be14a5c2c3a851a54fb?s=128',
            'name': 'Brent Lineberry',
            'url': 'https://orangegnome.com',
            'urlDisplay': 'Orange Gnome',
            'otherProfiles': [
                {
                    'url': 'https://twitter.com/BrentLineberry',
                    'urlDisplay': 'Twitter',
                },
                {
                    'url': 'https://www.strava.com/athletes/BrentLineberry',
                    'urlDisplay': 'Strava',
                },
                {
                    'url': 'https://www.instagram.com/BrentLineberry',
                    'urlDisplay': 'Instagram',
                },
            ]
        }
    }
    return render(request, 'pages/home.html', context)