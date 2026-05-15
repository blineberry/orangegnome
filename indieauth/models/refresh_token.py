from indieauth.models import TokenBase


class RefreshToken(TokenBase):
    TOKEN_MIN = 128
    TOKEN_MAX = 256
    DEFAULT_LIFETIME_SEC = 30 * 24 * 60 * 60 # 30 days
    
    def update_scope(self, requested_scope:str)->str:
        # The client may request a token with the same or fewer scopes than the 
        # original access token. If omitted, is treated as equal to the original 
        # scopes granted.

        if requested_scope is None:
            return self.scope
        
        new_scopes = []
        old_scopes = self.scope.split(" ")
        requested_scopes = requested_scope.split(" ")

        for scope in requested_scopes:
            if scope in old_scopes:
                new_scopes.append(scope)

        return (" ").join(new_scopes)
    
    def to_verification_response(self)->dict:
        response = super().to_verification_response()
        response["token_type"] = "refresh_token"
        return response