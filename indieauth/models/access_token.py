from indieauth.models import TokenBase
from indieauth.models.auth_token_base import canonicalize_url
from profiles.models import Profile


class AccessToken(TokenBase):
    TOKEN_MIN = 64
    TOKEN_MAX = 128
    DEFAULT_LIFETIME_SEC = 24 * 60 * 60 # 24 hours
    
    def to_token_response(self, refresh_token:str=None)->dict:
        scopes:list[str] = self.scope.split(" ")
        profile:Profile = self.user.profile

        response = {
            "access_token": self.token,
            "token_type": "Bearer",
            "scope": self.scope,
            "me": canonicalize_url(profile.url)
        }

        if refresh_token is not None:
            response["refresh_token"] = refresh_token

        if self.expires_in():
            response["expires_in"] = self.expires_in()

        if "profile" not in scopes:
            return response
        
        response["profile"] = self.profile_to_dict(profile)  

        return response

    
    def to_userinfo_response(self):
        scopes:list[str] = self.scope.split(" ")
        profile:Profile = self.user.profile

        response = {}

        if "profile" not in scopes:
            return response
        
        response = self.profile_to_dict(profile)        
        return response
    
    def get_issued_unix_time(self):
        return int(self.issued_utc.timestamp())
    
    def get_expires_unix_time(self):
        if self.expires_utc is None:
            return
        
        return int(self.expires_utc.timestamp())
    
    def get_scopes(self):
        return self.scope.split(" ")
    
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
    
    def to_verification_response(self)->dict:
        response = super().to_verification_response()
        response["token_type"] = "access_token"
        return response