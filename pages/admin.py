from django.contrib import admin
from .models import Person, Profile

class ProfileInline(admin.TabularInline):
    model = Profile
#    extra = 3

class PersonAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]


# Register your models here.
admin.site.register(Person, PersonAdmin)