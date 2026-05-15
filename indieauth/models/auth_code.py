import base64
import hashlib

from django.db import models
from django.utils import timezone

from indieauth.models import AuthTokenBase
from indieauth.models.server_metadata import ServerMetadata
from profiles.models import Profile


class AuthCode(AuthTokenBase):
    CODE_MIN = 16
    CODE_MAX = 45
    DEFAULT_LIFETIME_SEC = 5 * 60

    code = models.CharField(max_length=CODE_MAX, unique=True)
    redirect_uri = models.URLField()
    code_challenge = models.CharField(max_length=255)
    code_challenge_method = models.CharField(max_length=10)

    @classmethod
    def create(cls):
        code = cls()
        code.code = code.generate_code()
        return code

    def generate_code(self):
        return self.generate_token()
    
    def get_token_min(self):
        return self.CODE_MIN
    
    def get_token_max(self):
        return self.CODE_MAX

    def is_expired(self):
        now = timezone.now()

        timespan = now - self.issued_utc 
        return timespan.seconds > AuthCode.DEFAULT_LIFETIME_SEC
    
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
        
        response["profile"] = self.profile_to_dict(profile)        
        return response