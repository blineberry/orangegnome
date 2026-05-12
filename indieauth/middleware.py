from orangegnome import settings


def indieauth_middleware(get_response):
    metadata = settings.INDIEAUTH_METADATA
    auth = settings.INDIEAUTH_AUTH
    token = settings.INDIEAUTH_TOKEN

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        if request.path == '/':
            links:list[str] = []

            existing_links = response.get("Link", "")
            if existing_links is not None and existing_links.strip() != '':
                links = existing_links.split(',')

            links.append(f'<{ metadata }>; rel=indieauth-metadata')
            links.append(f'<{ auth }>; rel=indieauth_auth')

            response["Link"] = (",").join(links)

        return response

    return middleware