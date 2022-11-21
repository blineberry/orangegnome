from django.test import TestCase
from http import HTTPStatus

# Test the robots.txt file
class RobotsTest(TestCase):
    
    # GET /robots.txt, assert plain text document starting with 
    # "User-Agent: *" is returned
    def test_get(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")
        lines = response.content.decode().splitlines()
        self.assertEqual(lines[0], "User-Agent: *")

    # POST /robots.txt, assert method is not allowed
    def test_post(self):
        response = self.client.post("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)