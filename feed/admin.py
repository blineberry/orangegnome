from django.contrib import admin
from .models import Tag
from django import forms

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',)}
    readonly_fields = ('test',)
    fieldsets = ((None, { 'fields': ('name', 'slug', 'test')}),)

admin.site.register(Tag, TagAdmin)