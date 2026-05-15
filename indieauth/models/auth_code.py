import base64
import hashlib

from django.db import models
from django.utils import timezone

from indieauth.models import AuthTokenBase
from indieauth.viewmodels import AuthSubmissionVM
from profiles.models import Profile

CODE_CHALLENGE_METHODS = ["S256"]

def is_code_challenge_supported(method:str)->bool:
    return method in CODE_CHALLENGE_METHODS

def verify_challenge_code(code:str, challenge:str, method:str)->bool:
    if not is_code_challenge_supported(method):
            return False
        
    if method == "S256":
        result = hashlib.sha256(code.encode('utf-8')).digest()
        result = base64.urlsafe_b64encode(result).decode('utf-8')
        result = result.replace('=', '')
        return challenge == result
    
    return False

class AuthCode(AuthTokenBase):
    class CodeChallengeMethod(models.TextChoices):
        S256="S256"

    CODE_MIN = 16
    CODE_MAX = 45
    DEFAULT_LIFETIME_SEC = 5 * 60

    code = models.CharField(max_length=CODE_MAX, unique=True)
    redirect_uri = models.URLField()
    code_challenge = models.CharField(max_length=255)
    code_challenge_method = models.CharField(choices=CodeChallengeMethod, max_length=10)

    @classmethod
    def create(cls):
        code = cls()
        code.code = code.generate_code()
        return code
    
    @classmethod
    def from_auth_submission_vm(cls, vm:AuthSubmissionVM, user_id):
        code = cls.create()
        code.client_id = vm.values.get("client_id")
        code.redirect_uri = vm.values.get("redirect_uri")
        code.user_id = user_id
        code.code_challenge_method = vm.values.get("code_challenge_method")
        code.code_challenge = vm.values.get("code_challenge")
        code.scope = vm.values.get("scope", "")
        
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
    
    is_expired.boolean = True
    
    def verify_challenge_code(self, code_verifier:str)->bool:
        return verify_challenge_code(code_verifier, self.code_challenge, self.code_challenge_method)
    
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