from urllib.parse import urlsplit

from indieauth.models import AuthRequest, ClientMetadata


class AuthRequestVM():    
    client_name = ""
    client_url = ""
    scopes = []
    requested_scopes = []

    def __init__(self, request:AuthRequest, client:ClientMetadata):
        self.client_url = request.client_id
        self.client_name = urlsplit(self.client_url).netloc

        if client is not None and client.client_name is not None and client.client_name.trim() != '':
            self.client_name = client.client_name

        self.scopes = AuthRequest.SCOPES
        
        if request.scope is not None:
            self.requested_scopes = request.scope.split(" ")