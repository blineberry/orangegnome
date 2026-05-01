from django.contrib import admin
from .models import Profile, LinkedProfile, MetaTag

class LinkedProfileInline(admin.TabularInline):
    model = LinkedProfile
#    extra = 3

class MetaTagInline(admin.TabularInline):
    model = MetaTag
    extra = 0

class ProfileAdmin(admin.ModelAdmin):
    inlines = [LinkedProfileInline, MetaTagInline]



# Register your models here.
admin.site.register(Profile, ProfileAdmin)