from django.contrib import admin

from indieauth.models import AccessToken, AuthCode, RefreshToken

# Register your models here.
class AuthCodeAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_token']
    list_display = ["client_id", "user", "is_expired"]
    list_filter = ["user"]
    search_fields = ["client_id"]

class AccessTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_token']
    list_display = ["client_id", "user", "is_expired", "expires_in"]
    list_filter = ["user", "expires_utc"]
    search_fields = ["client_id"]

class RefreshTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_token']
    list_display = ["client_id", "user", "is_expired", "expires_in"]
    list_filter = ["user", "expires_utc"]
    search_fields = ["client_id"]

admin.site.register(AuthCode, AuthCodeAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)