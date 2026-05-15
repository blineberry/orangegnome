import random
import string
from urllib.parse import urlsplit

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from profiles.models import Profile

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

class AuthTokenBase(models.Model):
    TOKEN_MIN = 0
    TOKEN_MAX = 0
    DEFAULT_LIFETIME_SEC = 0

    scope = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_utc = models.DateTimeField(default=timezone.now)
    client_id = models.URLField()

    def generate_token(self):
        length = random.choice(range(self.get_token_min(),self.get_token_max(),1))
        return ''.join(random.choices(string.ascii_lowercase, k=length))
        
    def get_token_min(self):
        return self.TOKEN_MIN
    
    def get_token_max(self):
        return self.TOKEN_MAX
    
    def get_default_lifetime_seconds(self):
        return self.DEFAULT_LIFETIME_SEC
    
    def profile_to_dict(self, profile:Profile)->dict:
        p = {}

        if profile.name is not None:
            p["name"] = profile.name

        if profile.url is not None:
            p["url"] = canonicalize_url(profile.url)
        
        if profile.photo is not None and profile.photo.name.strip() != '':
            p["photo"]= profile.photo.url

        return p

    class Meta:
        abstract = True