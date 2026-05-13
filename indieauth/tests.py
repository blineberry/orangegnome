from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup
from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from requests import Response

from indieauth.models import AuthRequest, ClientMetadata, ServerMetadata
from indieauth.viewmodels import AuthRequestVM
from indieauth.views import AuthView
from .services import canonicalize_url
from profiles.models import Profile

# Create your tests here.
class ServicesTestCase(TestCase):
    def setUp(self):
        return super().setUp()
    
    def test_canonicalize_url(self):
        self.assertEqual('https://example.com/', canonicalize_url("https://example.com"))
        self.assertEqual('https://example.com/', canonicalize_url("https://EXAMPLE.com/"))
        self.assertEqual('https://example.com/path', canonicalize_url("https://example.com/path"))
        self.assertEqual('https://example.com/path?query#fragment', canonicalize_url("https://example.com/path?query#fragment"))

class AuthRequestTestCase(TestCase):
    def test_is_client_id_valid(self):
        auth = AuthRequest({})

        # Clients are identified by a [URL]. 
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "notaurl"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://example.com/"
        self.assertTrue(auth.is_client_id_valid())

        # Client identifier URLs MUST have either an https or http scheme, 
        auth.client_id = "file://example.com"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "http://example.com/"
        self.assertTrue(auth.is_client_id_valid())
        auth.client_id = "https://example.com/"
        self.assertTrue(auth.is_client_id_valid())

        # MUST contain a path component, 
        auth.client_id = "https://example.com"
        self.assertFalse(auth.is_client_id_valid())

        # MUST NOT contain single-dot or double-dot path segments, 
        auth.client_id = "https://example.com/./"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://example.com/../"
        self.assertFalse(auth.is_client_id_valid())

        # MAY contain a query string component, 

        auth.client_id = "https://example.com/?id=1"
        self.assertTrue(auth.is_client_id_valid())

        # MUST NOT contain a fragment component, 
        auth.client_id = "https://example.com/#fragment"
        self.assertFalse(auth.is_client_id_valid())

        # MUST NOT contain a username or password component, and 
        auth.client_id = "https://user@example.com/"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://user:pass@example.com/"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://:pass@example.com/"
        self.assertFalse(auth.is_client_id_valid())

        # MAY contain a port. 
        auth.client_id = "https://example.com:443/"
        self.assertTrue(auth.is_client_id_valid())

        # Additionally, host names MUST be domain names or a loopback interface and 
        # MUST NOT be IPv4 or IPv6 addresses except for IPv4 127.0.0.1 or IPv6 [::1].
        auth.client_id = "https://127.0.0.1/"
        self.assertTrue(auth.is_client_id_valid())
        auth.client_id = "https://[::1]/"
        self.assertTrue(auth.is_client_id_valid())
        auth.client_id = "https://192.168.0.1/"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://[2001:db8::]/"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://127.0.0.1:80/"
        self.assertTrue(auth.is_client_id_valid())
        auth.client_id = "https://[::1]:80/"
        self.assertTrue(auth.is_client_id_valid())
        auth.client_id = "https://192.168.0.1:80/"
        self.assertFalse(auth.is_client_id_valid())
        auth.client_id = "https://[2001:db8::]:80/"
        self.assertFalse(auth.is_client_id_valid())

    def test_is_redirect_uri_valid(self):
        auth = AuthRequest({
            "client_id": "https://example.com/",
            "redirect_uri": "https://example.com/callback"
        })
        client = ClientMetadata()
        client.redirect_uris = []

        self.assertTrue(auth.is_redirect_uri_valid(client))

        # If the URL scheme, host or port of the redirect_uri in the request do not match that of the client_id, 
        # then the authorization endpoint SHOULD verify that the requested redirect_uri matches one of the redirect URLs published by the client, and SHOULD block the request from proceeding if not.
        auth.redirect_uri = "http://example.com/callback"
        self.assertFalse(auth.is_redirect_uri_valid(client))
        client.redirect_uris.append("http://example.com/callback")
        self.assertTrue(auth.is_redirect_uri_valid(client))

        auth.redirect_uri = "https://example.net/callback"
        self.assertFalse(auth.is_redirect_uri_valid(client))
        client.redirect_uris.append("https://example.net/callback")
        self.assertTrue(auth.is_redirect_uri_valid(client))

        auth.redirect_uri = "https://example.com:80/callback"
        self.assertFalse(auth.is_redirect_uri_valid(client))
        client.redirect_uris.append("https://example.com:80/callback")
        self.assertTrue(auth.is_redirect_uri_valid(client))        

class AuthViewTestCase(TestCase):
    view:AuthView = None
    request:HttpRequest = None
    
    def setUp(self):
        self.view = AuthView()
        self.request = HttpRequest()
        self.request.session = dict()
        self.request.user = User()
        self.request.GET = {
            "client_id": "https://example.com/",
            "redirect_uri": "https://example.com/callback",
            "code_challenge": "codechallenge"
        }

    @patch('indieauth.views.ClientMetadata.fetch')
    def test_get(self, fetch):        
        fetch.return_value = None       
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

        client = ClientMetadata()
        fetch.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

        client.redirect_uris = ["https://sub.example.com/callback"]
        fetch.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

        self.request.GET["redirect_uri"] = "https://sub.example.com/callback"
        fetch.return_value = None       
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 400)

        client = ClientMetadata()
        fetch.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 400)

        client.redirect_uris = ["https://sub.example.com/callback"]
        fetch.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

class DiscoveryTestCase(TestCase):
    client:Client = None

    def setUp(self):
        self.client = Client()
        return super().setUp()
        
    def test_header_links(self):
        response = self.client.get("/")
        link = response.headers.get("Link")

        self.assertIsNotNone(link)

        links = link.split(",")

        links_dict = {}
        for l in links:
            parts = l.split(";")
            links_dict[parts[1].strip()] = parts[0].strip()
        
        for s in ["rel=indieauth-metadata", "rel=authorization_endpoint", "rel=token_endpoint"]:
            self.assertTrue(s in links_dict.keys())

    def test_html_links(self):
        response = self.client.get("/")

        soup = BeautifulSoup(response.content, "html.parser")

        for s in ["indieauth-metadata", "authorization_endpoint", "token_endpoint"]:            
            self.assertIsNotNone(soup.find('link', {"rel":s}))

    def test_endpoints_in_metadata(self):
        response = self.client.get(reverse("indieauth-metadata"))

        content = response.json()

        self.assertIsNotNone(content.get("authorization_endpoint"))
        self.assertIsNotNone(content.get("token_endpoint"))
        
class AuthorizationRequestTestCase(TestCase):
    client:Client = None
    authorization_endpoint = "/indieauth/auth"
    user = None
    code_verifier = None
    get_data = {}
    post_data = {}

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(self.user)
        self.code_verifier = "aAAi96b43AGcInR_pxWrb8pFKN1z3w2d2YzKOrvEWAWXIRtK1y9QVPCve4LcDYjy0W15KjXUEQ6naKqQIY1-_7Ub2lovyV8EPQq3WAA6DzMq1k6c1qyYo8uZGhKsUULd"
        self.get_data = {
            "response_type": "code",
            "client_id": "https://example.com/",
            "redirect_uri": "https://example.com/callback",
            "state": "statevalue",
            "code_challenge": "GVdkWuZV3ovoFRqGELA85Ojv4jHe7tu2HC03RW4k-vw",
            "code_challenge_method": "S256",
            "me": "https://me.example.com/"
        }
        self.post_data = self.get_data
        self.post_data[AuthRequestVM.ACCEPT] = "Accept"
        return super().setUp()

    @staticmethod
    def create_client_metadata(client_id, redirect_uris):
        return {
            "json.return_value" : {
                "client_id": client_id,
                "redirect_uris": redirect_uris
            },
            "status_code": 200,
            "url": client_id
        }
    @staticmethod
    def create_client_html(client_id, redirect_uris):
        html = f'<html><head><title></title>'

        for uri in redirect_uris:
            html += f'<link rel="redirect_uri" href="{uri}">'
        
        html += '</head><body></body></html>'
        
        return {
            "json": Mock(side_effect=ValueError()),
            "content": html,
            "status_code": 200,
            "url": client_id,
            "headers": {}
        }
    
    @patch('indieauth.models.request')
    def test_get_returns_view(self, request):
        response = self.client.get(self.authorization_endpoint, data=self.get_data)

        self.assertEqual(response.templates[0].name, "indieauth/auth.html")        
    
    def test_get_authenticated_user_required(self):
        self.client.logout()

        response = self.client.get(self.authorization_endpoint, data=self.get_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("admin:login", query={"next": self.authorization_endpoint}))

    def test_get_pkce_required(self):
        del self.get_data["code_challenge"]
        
        response = self.client.get(self.authorization_endpoint, data=self.get_data)
        
        self.assertEqual(response.status_code, 400)

    @patch('indieauth.models.request')
    def test_get_valid_client_id_required(self,request):        
        request.return_value = Mock(Response)
        attrs = {'json.return_value' : {}}
        request.return_value.configure_mock(**attrs)

        invalid_client_ids = [
            "notaurl",
            "file://example.com",
            "https://example.com",
            "https://example.com/./",
            "https://example.com/../",
            "https://example.com/#fragment",
            "https://user@example.com/",
            "https://user:pass@example.com/"
            "https://:pass@example.com/",
            "https://192.168.0.1/",
            "https://[2001:db8::]/",
            "https://192.168.0.1:80/",
            "https://[2001:db8::]:80/",
        ]

        valid_client_ids = [
            "http://example.com/",
            "https://example.com/",
            "https://example.com/path",
            "https://example.com/?id=1",
            "https://example.com:443/",
            "https://127.0.0.1/",
            "https://[::1]/",
            "https://127.0.0.1:443/",
            "https://[::1]:443/",
        ]

        for id in invalid_client_ids:
            self.get_data["client_id"] = id
            self.get_data["redirect_uri"] = id + "/callback"
            response = self.client.get(self.authorization_endpoint, data=self.get_data)
            self.assertEqual(400, response.status_code)

        for id in valid_client_ids:
            self.get_data["client_id"] = id
            self.get_data["redirect_uri"] = id + "/callback"
            response = self.client.get(self.authorization_endpoint, data=self.get_data)
            self.assertEqual(200, response.status_code, f'{id}: {response.content}')

        del self.get_data["client_id"]
        response = self.client.get(self.authorization_endpoint, data=self.get_data)
        self.assertEqual(400, response.status_code)

    @patch('indieauth.models.request')
    def test_get_valid_redirect_url_required(self, request):
        request.return_value = Mock(Response)
        attrs =  self.create_client_metadata(self.get_data.get("client_id"), [])

        # default redirect_uri = https://example.com/callback
        scenarios = [
            ("http://example.com/callback", attrs, 400), # different scheme, not in client metadata
            ("https://example.org/callback", attrs, 400), # different host, not in client metadata
            ("http://example.com/callback", self.create_client_metadata(
                self.get_data.get("client_id"),
                ["http://example.com/callback"]), 200), # different scheme, in client metadata
            ("https://example.org/callback", self.create_client_metadata(
                self.get_data.get("client_id"),
                ["https://example.org/callback"]), 200), # different host, in client metadata
            ("http://example.com/callback", self.create_client_html(self.get_data.get("client_id"),[]), 400), # different scheme, not in client html
            ("https://example.org/callback", self.create_client_html(self.get_data.get("client_id"),[]), 400), # different host, not in client html
            ("http://example.com/callback", self.create_client_html(self.get_data.get("client_id"),["http://example.com/callback"]), 200), # different scheme, in client html
            ("https://example.org/callback", self.create_client_html(self.get_data.get("client_id"),["https://example.org/callback"]), 200), # different host, in client html
        ]

        for s in scenarios:
            self.get_data["redirect_uri"] = s[0]
            request.return_value = Mock(Response, **s[1])
            response = self.client.get(self.authorization_endpoint, data=self.get_data)
            self.assertEqual(s[2], response.status_code, f'{s}: {response.content}')

    def test_post_returns_redirect(self):
        response = self.client.post(self.authorization_endpoint, self.post_data)
        
        self.assertEqual(302, response.status_code)

    def test_post_requires_csrf(self):
        self.client = Client(enforce_csrf_checks=True)
        
        response = self.client.post(self.authorization_endpoint, self.post_data)
        
        self.assertEqual(403, response.status_code)


    def test_post_authenticated_user_required(self):
        self.client.logout()

        response = self.client.post(self.authorization_endpoint, data=self.post_data)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, reverse("admin:login", query={"next": self.authorization_endpoint}))

    def test_post_pkce_required(self):
        del self.post_data["code_challenge"]
        
        response = self.client.post(self.authorization_endpoint, data=self.post_data)
        
        self.assertEqual(response.status_code, 400)

    @patch('indieauth.models.request')
    def test_post_valid_client_id_required(self,request):        
        request.return_value = Mock(Response)
        attrs = {'json.return_value' : {}}
        request.return_value.configure_mock(**attrs)

        invalid_client_ids = [
            "notaurl",
            "file://example.com",
            "https://example.com",
            "https://example.com/./",
            "https://example.com/../",
            "https://example.com/#fragment",
            "https://user@example.com/",
            "https://user:pass@example.com/"
            "https://:pass@example.com/",
            "https://192.168.0.1/",
            "https://[2001:db8::]/",
            "https://192.168.0.1:80/",
            "https://[2001:db8::]:80/",
        ]

        valid_client_ids = [
            "http://example.com/",
            "https://example.com/",
            "https://example.com/path",
            "https://example.com/?id=1",
            "https://example.com:443/",
            "https://127.0.0.1/",
            "https://[::1]/",
            "https://127.0.0.1:443/",
            "https://[::1]:443/",
        ]

        for id in invalid_client_ids:
            self.post_data["client_id"] = id
            self.post_data["redirect_uri"] = id + "/callback"
            response = self.client.post(self.authorization_endpoint, data=self.post_data)
            self.assertEqual(400, response.status_code)

        for id in valid_client_ids:
            self.post_data["client_id"] = id
            self.post_data["redirect_uri"] = id + "/callback"
            response = self.client.post(self.authorization_endpoint, data=self.post_data)
            self.assertEqual(302, response.status_code)

        del self.post_data["client_id"]
        response = self.client.post(self.authorization_endpoint, data=self.post_data)
        self.assertEqual(400, response.status_code)

    @patch('indieauth.models.request')
    def test_post_valid_redirect_url_required(self, request):
        request.return_value = Mock(Response)
        attrs =  self.create_client_metadata(self.post_data.get("client_id"), [])

        # default redirect_uri = https://example.com/callback
        scenarios = [
            ("http://example.com/callback", attrs, 400), # different scheme, not in client metadata
            ("https://example.org/callback", attrs, 400), # different host, not in client metadata
            ("http://example.com/callback", self.create_client_metadata(
                self.post_data.get("client_id"),
                ["http://example.com/callback"]), 302), # different scheme, in client metadata
            ("https://example.org/callback", self.create_client_metadata(
                self.post_data.get("client_id"),
                ["https://example.org/callback"]), 302), # different host, in client metadata
            ("http://example.com/callback", self.create_client_html(self.post_data.get("client_id"),[]), 400), # different scheme, not in client html
            ("https://example.org/callback", self.create_client_html(self.post_data.get("client_id"),[]), 400), # different host, not in client html
            ("http://example.com/callback", self.create_client_html(self.post_data.get("client_id"),["http://example.com/callback"]), 302), # different scheme, in client html
            ("https://example.org/callback", self.create_client_html(self.post_data.get("client_id"),["https://example.org/callback"]), 302), # different host, in client html
        ]

        for s in scenarios:
            self.post_data["redirect_uri"] = s[0]
            request.return_value = Mock(Response, **s[1])
            response = self.client.post(self.authorization_endpoint, data=self.post_data)
            self.assertEqual(s[2], response.status_code, f'{s}: {response.content}')

class RedeemTheAuthorizationCodeTestCase(TestCase):
    client = None
    auth_endpoint = None
    token_endpoint = None
    auth_data = None
    post_data = None
    code_verifier = None

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_login(user)
        Profile.objects.create(user=user, url="https://me.example.com").save()
        self.code_verifier = "aAAi96b43AGcInR_pxWrb8pFKN1z3w2d2YzKOrvEWAWXIRtK1y9QVPCve4LcDYjy0W15KjXUEQ6naKqQIY1-_7Ub2lovyV8EPQq3WAA6DzMq1k6c1qyYo8uZGhKsUULd"        
        self.auth_endpoint = reverse("indieauth:auth")
        self.token_endpoint = reverse("indieauth:token")
        self.auth_data = {
            "response_type": "code",
            "client_id": "https://example.com/",
            "redirect_uri": "https://example.com/callback",
            "state": "statevalue",
            "code_challenge": "GVdkWuZV3ovoFRqGELA85Ojv4jHe7tu2HC03RW4k-vw",
            "code_challenge_method": "S256",
            "me": "https://me.example.com/",
            "scope": "profile",
            AuthRequestVM.ACCEPT: "Accept"
        }
        code = self.get_authorization_code()
        self.post_data = self.get_post_data(code)

        return super().setUp()
    
    def get_authorization_code(self)->str:
        response = self.client.post(self.auth_endpoint, data=self.auth_data)
        url_parts = urlsplit(response.url)
        qs = parse_qs(url_parts.query)
        return qs.get("code")
    
    def get_post_data(self, code:str):
        return {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.auth_data.get("client_id"),
            "redirect_uri":self.auth_data.get("redirect_uri"),
            "code_verifier": self.code_verifier
        }
    
    def test_auth_returns_profile_url(self):
        response = self.client.post(self.auth_endpoint, data=self.post_data)
        
        content = response.json()
        self.assertIsNotNone(content.get("me"))
        self.assertIsNotNone(content.get("profile"))

    def test_auth_scope_optional(self):
        del self.auth_data["scope"]
        code = self.get_authorization_code()
        post_data = self.get_post_data(code)

        response = self.client.post(self.auth_endpoint, data=post_data)

        content = response.json()
        self.assertIsNotNone(content.get("me"))
        self.assertIsNone(content.get("profile"))

    def test_auth_requires_valid_code(self):
        self.post_data["code"] = "invalidcode"
        response = self.client.post(self.auth_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
    
    def test_auth_code_cannot_be_reused(self):
        self.client.post(self.auth_endpoint, data=self.post_data)
        response = self.client.post(self.auth_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
    
    def test_auth_client_id_match(self):
        self.post_data["client_id"] += "_invalid"
        response = self.client.post(self.auth_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
    
    def test_auth_redirect_uri_match(self):
        self.post_data["redirect_uri"] += "_invalid"
        response = self.client.post(self.auth_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)

    def test_auth_code_challenge(self):
        self.post_data["code_verifier"] += "_invalid"
        response = self.client.post(self.auth_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)

    def test_token_returns_response(self):
        response = self.client.post(self.token_endpoint, data=self.post_data)

        content = response.json()
        self.assertIsNotNone(content.get("access_token"))
        self.assertIsNotNone(content.get("me"))
        self.assertIsNotNone(content.get("profile"))

    def test_token_requires_scope(self):
        del self.auth_data["scope"]
        code = self.get_authorization_code()
        post_data = self.get_post_data(code)

        response = self.client.post(self.token_endpoint, data=post_data)

        self.assertEqual(400, response.status_code)

    def test_token_requires_valid_code(self):
        self.post_data["code"] = "invalidcode"
        response = self.client.post(self.token_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
    
    def test_token_code_cannot_be_reused(self):
        self.client.post(self.token_endpoint, data=self.post_data)
        response = self.client.post(self.token_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
    
    def test_token_client_id_match(self):
        self.post_data["client_id"] += "_invalid"
        response = self.client.post(self.token_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
    
    def test_token_redirect_uri_match(self):
        self.post_data["redirect_uri"] += "_invalid"
        response = self.client.post(self.token_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)

    def test_token_code_challenge(self):
        self.post_data["code_verifier"] += "_invalid"
        response = self.client.post(self.token_endpoint, data=self.post_data)
        
        self.assertEqual(400, response.status_code)
