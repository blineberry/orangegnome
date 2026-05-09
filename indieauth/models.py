import ipaddress
import re
from urllib.parse import urlsplit

from django.db import models

# Create your models here.
class ClientMetadata():
    redirect_uris = []

class AuthRequest():    
    CODE_CHALLENGE_METHODS_SUPPORTED = ['256']
    SCOPES = ['profile']
    
    def __init__(self, get_request):
        self.response_type = get_request.get('response_type')
        self.client_id = get_request.get('client_id')
        self.redirect_uri = get_request.get('redirect_uri')
        self.state = get_request.get('state')
        self.code_challenge = get_request.get('code_challenge')
        self.code_challenge_method = get_request.get('code_challenge_method')
        self.scope = get_request.get('scope')
        self.me = get_request.get('me')

    # https://indieauth.spec.indieweb.org/#client-identifier
    def is_client_id_valid(self)->bool:
        # Clients are identified by a [URL].
        if self.client_id is None:
            return False
        
        split = urlsplit(self.client_id)
        
        # Client identifier URLs MUST have either an https or http scheme,
        valid_schemes = ['http','https']
        if split.scheme not in valid_schemes:
            return False
        
        # MUST contain a path component,
        if split.path == '':
            return False

        # MUST NOT contain single-dot or double-dot path segments,
        segments = split.path.split(sep="/")
        invalid_segments = [".", ".."]
        for segment in segments:
            if segment in invalid_segments:
                return False
            
        # MAY contain a query string component, 
        # MUST NOT contain a fragment component, 
        if split.fragment != '':
            return False
        
        # MUST NOT contain a username or password component, and 
        if split.username != None:
            return False
        
        if split.password != None:
            return False
        
        # MAY contain a port. Additionally, 
        # host names MUST be domain names or a loopback interface and MUST NOT be IPv4 or IPv6 addresses except for IPv4 127.0.0.1 or IPv6 [::1].        
        valid_ips = ["127.0.0.1", "[::1]"]        
        if split.netloc not in valid_ips:
            # ipv6
            pattern = re.compile("^\[[a-zA-Z0-9:]+\](:[0-9]+){0,1}")
            if pattern.match(split.netloc):
                if split.netloc[-1] == "]":
                    return False
                
                ip, sep, port = split.netloc.rpartition(":")
                if ip not in valid_ips:
                    return False
            else:
                host = split.netloc.rsplit(":")[0]
                if host not in valid_ips:
                    try:
                        ipaddress.ip_address(host)
                        return False
                    except:
                        pass                

        return True
    
    def is_redirect_uri_valid(self, client:ClientMetadata)->bool:
        redirect_parts = urlsplit(self.redirect_uri)
        client_id_parts = urlsplit(self.client_id)
        
        # If the URL scheme, host or port of the redirect_uri in the request do not match that of the client_id, 
        if (redirect_parts.scheme == client_id_parts.scheme and
            redirect_parts.netloc == client_id_parts.netloc):
            return True

        # then the authorization endpoint SHOULD verify that the requested redirect_uri matches one of the redirect URLs published by the client, and SHOULD block the request from proceeding if not.
        if client is None:
            return False
        
        return self.redirect_uri in client.redirect_uris
    



