from typing import Optional
from django.contrib import admin
from bs4 import BeautifulSoup
from django.http.request import HttpRequest
from .models import Webmention, PendingOutgoingWebmention, OutgoingWebmention,PendingIncomingWebmention,IncomingWebmention



# Register your models here.
class ReadOnlyAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None) -> bool:
        return False
    
class PendingOutgoingWebmentionAdmin(ReadOnlyAdmin):
    actions = ["process_pending_outgoing_webmentions"]

    @admin.action(description="Process selected webmentions")
    def process_pending_outgoing_webmentions(self, request, queryset):
        for obj in queryset:
            obj.process()

class OutgoingWebmentionAdmin(ReadOnlyAdmin):
    actions = ["try_notify_receivers"]

    @admin.action(description="Notify selected webmentions' receivers")
    def try_notify_receivers(self, request, queryset):
        for obj in queryset:
            obj.try_notify_receiver()

class PendingIncomingWebmentionAdmin(ReadOnlyAdmin):
    actions = ["process_pending_incoming_webmentions"]

    @admin.action(description="Process selected webmentions")
    def process_pending_incoming_webmentions(self, request, queryset):
        for obj in queryset:
            obj.process_and_save()

class IncomingWebmentionAdmin(ReadOnlyAdmin):
    actions = ["parse_content", "attach"]

    @admin.action(description="Parse selected webmentions' content")
    def parse_content(self, request, queryset):
        for obj in queryset:
            obj.try_parse_source_content_and_save()
    
    @admin.action(description="Attach webmentions to webmentionables")
    def attach(self, request, queryset):
        for obj in queryset:
            obj.try_attach_to_webmentionable()

admin.site.register(PendingOutgoingWebmention,PendingOutgoingWebmentionAdmin)
admin.site.register(OutgoingWebmention,OutgoingWebmentionAdmin)
admin.site.register(IncomingWebmention,IncomingWebmentionAdmin)
admin.site.register(PendingIncomingWebmention,PendingIncomingWebmentionAdmin)