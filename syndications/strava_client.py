import requests
from requests_oauthlib import OAuth2
from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qs
from swagger_client import ApiClient

class Token(object):
    def __init__(self, athlete_id=None, scopes=None, access_token=None, expires_at=None, expires_in=None, refresh_token=None):
        self.expires_at = expires_at
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.athlete_id = athlete_id
        self.scopes = scopes

class Athlete(object):
    def __init__(self, id=None, username=None):
        self.id=id
        self.username=username

class Client(object):
    authorize_uri = "https://www.strava.com/oauth/authorize"
    token_uri = "https://www.strava.com/oauth/token"
    state = None
    scopes = "activity:read"

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorize_url(self, state=None):
        self.state = state

        url_parts = urlsplit(self.authorize_uri)

        url = urlunsplit((url_parts[0], url_parts[1],url_parts[2], urlencode({
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": self.scopes,
            "state": state,
        }), url_parts[4]))

        return url   

    def parse_authorize_response(self, response):
        qs = parse_qs(urlsplit(response)[3])
        return qs['state'], qs['code'], qs['scope'],

    def try_get_tokens(self, authorize_response):
        state, code, scope = self.parse_authorize_response(authorize_response)

        if state != self.state:
            return False

        if self.scopes not in scope[0].split(','):
            return False

        response = requests.post(self.token_uri, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': "authorization_code"
        })

        if response.status_code is not 200:
            return False

        json = response.json()

        self.athlete = Athlete(id=json['athlete']['id'], username=json['athlete']['username'])
        self.token = Token(athlete_id=self.athlete.id, scopes=self.scopes, access_token=json['access_token'], expires_at=json['expires_at'], expires_in=json['expires_in'], refresh_token=json['refresh_token'])        

        return True
    
    def try_refresh_tokens(self, strava_token):
        response = requests.post(self.token_uri, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': strava_token.refresh_token,
            'grant_type': "refresh_token"
        })

        if response.status_code is not 200:
            return False

        json = response.json()

        self.athlete = Athlete(id=json['athlete']['id'], username=json['athlete']['username'])
        self.token = Token(athlete_id=self.athlete.id, scopes=self.scopes, access_token=json['access_token'], expires_at=json['expires_at'], expires_in=json['expires_in'], refresh_token=json['refresh_token'])        

        return True

    def get_athlete(self):
        response = requests.get("https://www.strava.com/api/v3/athlete", auth=OAuth2(client_id=self.client_id, token={
            "access_token": self.access_token.token,
            "token_type": "Bearer"
        }))

    def get_activities(self, before=None, after=None, activities=[], per_page=30, page=1):
        data = {
            'per_page': per_page,
            'page': page
        }
        if before is not None:
            data['before'] = before

        if after is not None:
            data['after'] = after
        
        response = requests.get("https://www.strava.com/api/v3/activities", auth=OAuth2(client_id=self.client_id, token={
            "access_token": self.access_token.token,
            "token_type": "Bearer"
        }), data=data)

        json = response.json()

        activities = activities + json

        if len(json) < per_page:
            return activities

        return self.get_activities(before=before, after=after,activities=activities, per_page=per_page, page=page+1)
