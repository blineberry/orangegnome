from django.contrib import admin
from .models import OutgoingContent, OutgoingWebmention,IncomingWebmention,AllowedDomain



# Register your models here.
class ReadOnlyAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None) -> bool:
        return False
    
class OutgoingContentAdmin(admin.ModelAdmin):
    actions = ["process_pending_outgoing_webmentions"]

    list_display = ["__str__", "tries"]

    @admin.action(description="Process selected webmentions")
    def process_pending_outgoing_webmentions(self, request, queryset):
        for obj in queryset:
            obj.process()

class OutgoingWebmentionAdmin(admin.ModelAdmin):
    actions = ["try_notify_receivers"]

    list_display = ["__str__", "success", "tries"]

    @admin.action(description="Notify selected webmentions' receivers")
    def try_notify_receivers(self, request, queryset):
        for obj in queryset:
            obj.try_notify_receiver()

class IncomingWebmentionAdmin(admin.ModelAdmin):
    #actions = ["fetch_source", "verify", "parse_content", "attach", "process", "approve"]
    actions = ["process", "approve", "allow_domain"]

    list_display = ["__str__", "is_content_fetched", "verified", "is_parsed", "is_attached", "approved", "tries"]

    @admin.action(description="Fetch the source content")
    def fetch_source(self, request, queryset):
        for obj in queryset:
            obj.try_fetch_source_content_and_save(True)

    @admin.action(description="Verify")
    def verify(self, request, queryset):
        for obj in queryset:
            obj.try_verify_webmention_and_save(True)

    @admin.action(description="Parse content")
    def parse_content(self, request, queryset):
        for obj in queryset:
            obj.try_parse_source_content_and_save(True)
    
    @admin.action(description="Attach webmentions to webmentionables")
    def attach(self, request, queryset):
        for obj in queryset:
            obj.try_attach_to_webmentionable_and_save(True)

    @admin.action(description="Process")
    def process(self, request, queryset):
        for obj in queryset:
            obj.process_and_save(True)

    @admin.action(description="Approve")
    def approve(self, request, queryset):
        for obj in queryset:
            obj.approve_and_save()

    @admin.action(description="Allowlist domain")
    def allow_domain(self, request, queryset):
        for obj in queryset:
            obj.add_domain_to_allowlist()

admin.site.register(OutgoingContent,OutgoingContentAdmin)
admin.site.register(OutgoingWebmention,OutgoingWebmentionAdmin)
admin.site.register(IncomingWebmention,IncomingWebmentionAdmin)
admin.site.register(AllowedDomain, admin.ModelAdmin)