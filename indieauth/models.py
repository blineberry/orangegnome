import base64
from datetime import timedelta
import hashlib
import random
import socket
import string
import ipaddress
import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import mf2py
from requests import Response, request

from orangegnome import settings
from profiles.models import Profile

# Create your models here.
class IndieAuthBase():
    @staticmethod
    def generate_random_string(min:int, max:int):
        length = random.choice(range(min,max,1))
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    @staticmethod 
    def profile_to_dict(profile:Profile)->dict:
        p = {}

        if profile.name is not None:
            p["name"] = profile.name

        if profile.url is not None:
            p["url"] = IndieAuthBase.canonicalize_url(profile.url)
        
        if profile.photo is not None and profile.photo.name.strip() != '':
            p["photo"]= profile.photo.url

        return p

    @staticmethod
    def canonicalize_url(url:str)->str:
        split = urlsplit(url)

        path = split.path
        netloc = split.netloc.lower()

        if path == '':
            path = '/'

        url = f'{split.scheme}://{netloc}{path}'

        if split.query != '':
            url += f'?{split.query}'

        if split.fragment != '':
            url += f'#{split.fragment}'

        return url


class ServerMetadata():
    issuer = settings.INDIEAUTH_ISSUER    
    scopes_supported =  ['profile']
    code_challenge_methods_supported = ['S256']

    def __init__(self, reverse):
        self.authorization_endpoint =  settings.SITE_URL + reverse('indieauth:auth')
        self.token_endpoint =  settings.SITE_URL + reverse('indieauth:token')
        self.introspection_endpoint =  settings.SITE_URL + reverse('indieauth:introspect')
        self.revocation_endpoint =  settings.SITE_URL + reverse('indieauth:revoke')
        self.userinfo_endpoint =  settings.SITE_URL + reverse('indieauth:userinfo')

    def to_json(self):
        return {
            "issuer": self.issuer,
            "scopes_supported": self.scopes_supported,
            "code_challenge_methods_supported": self.code_challenge_methods_supported,
            "authorization_endpoint": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "introspection_endpoint": self.introspection_endpoint,
            "revocation_endpoint": self.revocation_endpoint,
            "userinfo_endpoint": self.userinfo_endpoint
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
    def from_json(json, response, client_id):
        content_client_id = json.get("client_id")

        if content_client_id is None or content_client_id != client_id:
            return None

        client = ClientMetadata()
        client.client_id = json.get(content_client_id)
        client.client_name = json.get("client_name")
        client.client_uri = json.get("client_uri")
        client.logo_uri = json.get("logo_uri")
        client.redirect_uris = []
        
        redirect_uris = json.get("redirect_uris",[])

        for uri in redirect_uris:
            client.redirect_uris.append(urljoin(response.url, uri))
        
        return client
    
    # When a client chooses to serve a web page as its client_id, the client MAY 
    # publish one or more <link> tags or Link HTTP headers with a rel attribute 
    # of redirect_uri at the client_id URL to be used by the authorization 
    # server.
    @staticmethod
    def from_html(response:Response, client_id:str):
        client = ClientMetadata()
        client.client_id = client_id
        
        try:
            content = response.content

            mf2parser = mf2py.Parser(content)

            h_apps = mf2parser.to_dict(filter_by_type="h-app")

            if len(h_apps) > 0:
                client.name = h_apps[0].get("name", [])[0]
                client.logo_uri = h_apps[0].get("logo", [])[0]
                client.client_uri = h_apps[0].get("url", [])[0]
            
            client.redirect_uris = []
        except:
            pass      

        try:
            soup = BeautifulSoup(content, 'html.parser')

            for link in soup.find_all("link", {"rel": "redirect_uri"}):
                href = link.get("href")
                if href is not None and href.strip() != '':
                    client.redirect_uris.append(urljoin(response.url, href))
        except:
            pass    

        try:   
            link_header = response.headers.get("Link")
            if link_header is None:
                return client
            
            links = link_header.split(",")
            for l in links:
                parts = l.split(";")

                for pv in parts[1:]:
                    pv_parts = pv.split("=")

                    if len(pv_parts) != 2:
                        continue

                    if pv_parts[0].strip().lower() != "rel":
                        continue

                    value = pv_parts[1].lower()
                    if value != "redirect_uri" and value != "\"redirect_uri\"":
                        continue

                    client.redirect_uris.append(parts[0].strip()[1:-1])
        except:
            pass

        return client
        
    @staticmethod
    def fetch(client_id):
        if not ClientMetadata.should_fetch(client_id):
            return None
        
        response:Response = request("GET", client_id)

        try:
            response.raise_for_status()
        except:
            return None
        
        try:
            content = response.json()
            return ClientMetadata.from_json(content, response, client_id)
        except:
            try:
                return ClientMetadata.from_html(response, client_id)
            except:
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
        return IndieAuthBase.generate_random_string(AuthCode.CODE_MIN,AuthCode.CODE_MAX)

    def is_expired(self):
        now = timezone.now()

        timespan = now - self.issued_utc 
        return timespan.seconds > AuthCode.LIFESPAN_SEC
    
    def verify_challenge_code(self, code_verifier:str)->bool:
        if self.code_challenge_method not in ServerMetadata.code_challenge_methods_supported:
            return False
        
        if self.code_challenge_method == "S256":
            result = hashlib.sha256(code_verifier.encode('utf-8')).digest()
            result = base64.urlsafe_b64encode(result).decode('utf-8')
            result = result.replace('=', '')
            return self.code_challenge == result
        
        return False
    
    def to_profile_url_response(self):
        scopes:list[str] = self.scope.split(" ")
        profile:Profile = self.user.profile

        response = {
            "me": profile.url
        }

        if "profile" not in scopes:
            return response
        
        response["profile"] = IndieAuthBase.profile_to_dict(profile)        
        return response        
    
class AccessToken(models.Model, IndieAuthBase):
    TOKEN_MIN = 64
    TOKEN_MAX = 128

    token = models.TextField()
    scope = models.CharField(max_length=255)
    client_id = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_utc = models.DateTimeField(default=timezone.now)
    expires_utc = models.DateTimeField(null=True,blank=True)

    @staticmethod
    def generate_token():
        return IndieAuthBase.generate_random_string(AccessToken.TOKEN_MIN, AccessToken.TOKEN_MAX)
    
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
            "me": IndieAuthBase.canonicalize_url(profile.url)
        }

        if "profile" not in scopes:
            return response
        
        response["profile"] = IndieAuthBase.profile_to_dict(profile)        
        return response   
    
    def to_userinfo_response(self):
        scopes:list[str] = self.scope.split(" ")
        profile:Profile = self.user.profile

        response = {
            "me": IndieAuthBase.canonicalize_url(profile.url)
        }

        if "profile" not in scopes:
            return response
        
        response["profile"] = IndieAuthBase.profile_to_dict(profile)        
        return response   