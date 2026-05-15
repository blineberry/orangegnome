from datetime import timedelta

from django.db import models
from django.utils import timezone

from indieauth.models.auth_code import AuthCode
from indieauth.models.auth_token_base import AuthTokenBase
from profiles.models import Profile


class TokenBase(AuthTokenBase):
    token = models.TextField()
    expires_utc = models.DateTimeField(null=True,blank=True)

    @classmethod
    def create(cls, *args, **kwargs):
        token = cls(*args,**kwargs)
        token.token = token.generate_token()
        token.expires_utc = token.calculate_expires_utc()
        return token

    @classmethod
    def from_auth_code(cls, auth_code:AuthCode):
        token = cls.create()
        token.scope = auth_code.scope
        token.user = auth_code.user
        token.client_id = auth_code.client_id

        return token
    
    @classmethod
    def from_refresh_token(cls, refresh_token, updated_scope:str=None):
        token = cls.create()
        token.scope = refresh_token.scope if updated_scope is not None else updated_scope
        token.user = refresh_token.user
        token.client_id = refresh_token.client_id

        return token            
    
    def calculate_expires_utc(self):
        return timezone.now() + timedelta(seconds=self.get_default_lifetime_seconds())
    
    def expires_in(self):
        if self.expires_utc is None:
            return None
        
        timedelta = self.expires_utc - timezone.now()
        seconds = int(timedelta.total_seconds())
        
        return seconds
    
    def is_expired(self):
        if self.expires_utc is None:
            return False
        
        return timezone.now() >= self.expires_utc
    
    is_expired.boolean = True
    
    def to_verification_response(self)->dict:
        profile:Profile = self.user.profile

        if self.is_expired():
            return {
                "active": False
            }

        response = {
            "active": not self.is_expired(),
            "me": profile.url,
            "client_id": self.client_id,
            "scope": self.scope,
            "iat": self.get_issued_unix_time()
        }

        if self.expires_utc is not None:
            response["exp"] = self.get_expires_unix_time()

        return response 

    class Meta:
        abstract = True