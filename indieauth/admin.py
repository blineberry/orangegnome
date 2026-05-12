from django.contrib import admin

from indieauth.models import AccessToken

# Register your models here.
class AccessTokenAdmin(admin.ModelAdmin):
    readonly_fields = ['generate_code']

admin.site.register(AccessToken, AccessTokenAdmin)