from orangegnome import settings


def indieauth(request):
    if request.path == '/':
        return { 'indieauth': 
            {
                'metadata': settings.INDIEAUTH_TOKEN,
                'auth': settings.INDIEAUTH_AUTH, 
                'token': settings.INDIEAUTH_TOKEN, 
            }
        }