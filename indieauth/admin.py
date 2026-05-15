from django.contrib import admin

from indieauth.models import AccessToken, AuthCode, RefreshToken

# Register your models here.
class AuthCodeAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_token']

class AccessTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_token']

class RefreshTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_token']

admin.site.register(AuthCode, AuthCodeAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)