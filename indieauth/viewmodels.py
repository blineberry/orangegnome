from urllib.parse import urlsplit
from django.http import QueryDict
from indieauth.models import AuthCode, ClientMetadata

class AuthRequestVM():
    ACCEPT:str = "ACCEPT"
    values:QueryDict = QueryDict()
    client:ClientMetadata = None

    def client_id(self):
        return self.values.get("client_id")
    
    def client_url(self):
        return self.values.get("client_url")    
    
    def client_name(self):
        name = urlsplit(self.values.get("client_id")).netloc
    
        if self.client is not None and self.client.client_name is not None and self.client.client_name.strip() != '':
            name = self.client.client_name

        return name

    def response_type(self):
        return self.values.get("response_type")

    def redirect_uri(self):
        return self.values.get("redirect_uri")

    def state(self):
        return self.values.get("state")

    def code_challenge(self):
        return self.values.get("code_challenge")

    def code_challenge_method(self):
        return self.values.get("code_challenge_method")

    def me(self):
        return self.values.get("me")

    def scopes(self):
        return self.values.get("scope", "").split(" ")

    def __init__(self, values:QueryDict, client:ClientMetadata):
        self.values = values
        self.client = client

class AuthSubmissionVM():
    values:QueryDict = QueryDict() 
    issuer:str = None

    def __init__(self, values:QueryDict, issuer:str):
        self.values = values
        self.issuer = issuer

    def is_approved(self):
        return AuthRequestVM.ACCEPT in self.values.keys()
    
    def get_redirect_uri(self, auth_code=None):
        if not self.is_approved():
            return f'{self.values.get("redirect_uri")}?error=access_denied'
        
        if self.values.get("response_type") != 'code':
            return f'{self.values.get("redirect_uri")}?error=unsupported_response_type'
        
        if auth_code is None:
            raise ValueError("auth_code is required")
        
        return f'{self.values.get("redirect_uri")}?code={auth_code}&state={self.values.get("state")}&iss={self.issuer}'
    
    def should_generate_auth_code(self):
        if not self.is_approved():
            return False
        
        if self.values.get("response_type") != 'code':
            return False   

        return True 
        
    def create_auth_code(self, user_id):
        code = AuthCode()
        code.code = AuthCode.generate_code()
        code.client_id = self.values.get("client_id")
        code.redirect_uri = self.values.get("redirect_uri")
        code.user_id = user_id
        
        return code