from django.contrib import admin
from .models import Post, Category, Tag
from django.utils import timezone

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = ('published',)
    exclude = ('is_published',)

    def _unpublish(self, obj):
        obj.is_published = False
        return obj

    def _publish(self, obj):
        if obj.is_published:
            return obj

        obj.is_published = True
        obj.published = timezone.now()
        return obj

    def save_model(self, request, obj, form, change):
        if '_unpublish' in request.POST:
            obj = self._unpublish(obj)

        if '_publish' in request.POST:
            obj = self._publish(obj)

        return super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)