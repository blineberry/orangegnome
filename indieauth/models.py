import base64
from datetime import timedelta
import hashlib
from json import JSONEncoder
import random
import socket
import string

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import ipaddress
import re
from urllib.parse import urlsplit
from indieauth.services import canonicalize_url
from orangegnome import settings
from profiles.models import Profile

# Create your models here.
class ServerMetadata():
    issuer = settings.INDIEAUTH_ISSUER    
    scopes_supported =  ['profile']
    code_challenge_methods_supported = ['S256']

    def __init__(self, reverse):
        self.authorization_endpoint =  settings.SITE_URL + reverse('indieauth:auth')
        self.token_endpoint =  settings.SITE_URL + reverse('indieauth:token')
        self.introspection_endpoint =  settings.SITE_URL + reverse('indieauth:introspect')

    def to_json(self):
        return {
            "issuer": self.issuer,
            "scopes_supported": self.scopes_supported,
            "code_challenge_methods_supported": self.code_challenge_methods_supported,
            "authorization_endpont": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "introspection_endpont": self.introspection_endpoint
        }


    
class ClientMetadata():
    client_id = ""
    client_name = None
    client_uri = ""
    logo_uri = None
    redirect_uris = None

    @staticmethod
    def should_fetch(client_id):
        try:
            split = urlsplit(client_id)
            unauthorized_netloc = [
                '127.0.0.0', 
                '127.0.0.1', 
                '127.0.0.2'
                '127.0.0.3'
                '127.0.0.4'
                '127.0.0.5'
                '127.0.0.6'
                '127.0.0.7'
                '127.0.0.8'
                '[::1]']

            if split.netloc in unauthorized_netloc:
                return False
            
            addrinfo = socket.getaddrinfo(split.netloc, None, socket.AF_UNSPEC)

            for i in addrinfo:
                for ip in i[4]:
                    if ip in unauthorized_netloc:
                        return False
                    
            return True
            
        except:
            return False
    @staticmethod
    def fetch(client_id):
        return None

class AuthRequest():    
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
            pattern = re.compile(r"^\[[a-zA-Z0-9:]+\](:[0-9]+){0,1}")
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
    
class AuthCode(models.Model):
    CODE_MIN = 16
    CODE_MAX = 45
    LIFESPAN_SEC = 5 * 60

    code = models.CharField(max_length=CODE_MAX, unique=True)
    client_id = models.URLField()
    redirect_uri = models.URLField()
    issued_utc = models.DateTimeField(default=timezone.now)
    code_challenge = models.CharField(max_length=255)
    code_challenge_method = models.CharField(max_length=10)
    scope = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @staticmethod
    def generate_code():
        length = random.choice(range(AuthCode.CODE_MIN,AuthCode.CODE_MAX,1))
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def is_expired(self):
        now = timezone.now()

        timespan = now - self.issued_utc 
        return timespan.seconds > AuthCode.LIFESPAN_SEC
    
    def verify_challenge_code(self, code_verifier:str)->bool:
        if self.code_challenge_method not in ServerMetadata.code_challenge_methods_supported:
            return False
        
        if self.code_challenge_method == "S256":
            return self.code_challenge == hashlib.sha256(code_verifier.encode('utf-8')).digest().hex()
        
        return False
    
    def to_profile_url_response(self):
        scopes:list[str] = self.scope.split(" ")
        profile:Profile = self.user.profile

        response = {
            "me": profile.url
        }

        if "profile" in scopes:
            response["profile"] = {
                "name": profile.name,
                "url": canonicalize_url(profile.url),
                "photo": profile.photo
            }
        
        return response        
    
class AccessToken(models.Model):
    TOKEN_MIN = 64
    TOKEN_MAX = 128

    token = models.TextField()
    scope = models.CharField(max_length=255)
    client_id = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_utc = models.DateTimeField(default=timezone.now)
    expires_utc = models.DateTimeField(null=True,blank=True)

    @staticmethod
    def generate_code():
        length = random.choice(range(AccessToken.TOKEN_MIN,AccessToken.TOKEN_MAX,1))
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    @staticmethod
    def get_default_expires():
        return timezone.now() + timedelta(minutes=20)
    
    def expires_in(self):
        if self.expires_utc is None:
            return None
        
        return (self.expires_utc - self.issued_utc).seconds
    
    def to_token_response(self):
        scopes:list[str] = self.scope.split(" ")
        profile:Profile = self.user.profile

        response = {
            "access_token": self.token,
            "token_type": "Bearer",
            "scope": self.scope,
            "me": canonicalize_url(profile.url)
        }

        if "profile" in scopes:
            response["profile"] = {
                "name": profile.name,
                "url": canonicalize_url(profile.url),
                "photo": profile.photo
            }
        
        return response