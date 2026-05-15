from django.conf import settings

from indieauth.models.auth_code import CODE_CHALLENGE_METHODS

class ServerMetadata():
    issuer = settings.INDIEAUTH_ISSUER    
    scopes_supported =  ['profile']
    code_challenge_methods_supported = CODE_CHALLENGE_METHODS

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