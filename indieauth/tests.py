from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase

from indieauth.models import AuthRequest, ClientMetadata
from indieauth.views import AuthView
from .services import canonicalize_url

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
        self.request.GET = {
            "client_id": "https://example.com/",
            "redirect_uri": "https://example.com/callback"
        }

    @patch('indieauth.views.get_client_metadata')
    def test_get(self, get_client_metadata):        
        get_client_metadata.return_value = None       
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

        client = ClientMetadata()
        get_client_metadata.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

        client.redirect_uris = ["https://sub.example.com/callback"]
        get_client_metadata.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)

        self.request.GET["redirect_uri"] = "https://sub.example.com/callback"
        get_client_metadata.return_value = None       
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 400)

        client = ClientMetadata()
        get_client_metadata.return_value = client
        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 400)

        client.redirect_uris = ["https://sub.example.com/callback"]
        get_client_metadata.return_value = client

        response = self.view.get(self.request)
        self.assertEqual(response.status_code, 200)




