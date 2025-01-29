from django.contrib import admin
from .models import Tag, Syndication
from django import forms
from django.utils import timezone
from syndications.admin import SyndicatableAdmin as SAAdmin

# Register your models here.
class SyndicationInline(admin.TabularInline):
    model = Syndication
    extra = 1

class PublishableMixin():
    is_published = 'is_published'
    published_date = 'published'

    def should_publish(self, request, obj, form, change):
        if not getattr(obj, self.is_published):
            return False

        if self.is_published not in form.changed_data:
            return False

        return True

    def publish(self, request, obj, form, change):
        if not self.should_publish(request, obj, form, change):
            return obj

        if getattr(obj, self.published_date) is None:
            setattr(obj,self.published_date,timezone.now())

        return obj

class PublishableAdmin(PublishableMixin, admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        get_data = super(PublishableAdmin, self).get_changeform_initial_data(request)
        
        if hasattr(request.user, "profile"):
            get_data['author'] = request.user.profile.pk
        
        return get_data
    
    def save_model(self, request, obj, form, change):
        obj = self.publish(request, obj, form, change)

        return super().save_model(request, obj, form, change)

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',)}
    readonly_fields = ('test',)
    fieldsets = ((None, { 'fields': ('name', 'slug', 'test')}),)

class SyndicatableAdmin(PublishableAdmin, SAAdmin):
    inlines = [SyndicationInline]

admin.site.register(Tag, TagAdmin)