from django.contrib import admin
from .models import Profile, LinkedProfile

class LinkedProfileInline(admin.TabularInline):
    model = LinkedProfile
#    extra = 3

class ProfileAdmin(admin.ModelAdmin):
    inlines = [LinkedProfileInline]


# Register your models here.
admin.site.register(Profile, ProfileAdmin)