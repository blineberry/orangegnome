from django.contrib import admin
from .models import Post, Category, Tag
from django.utils import timezone

class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('title',)}
    readonly_fields = ('published',)

    def save_model(self, request, obj, form, change):
        if not obj.is_published:
            obj.published = None
            return super().save_model(request, obj, form, change)
        
        if 'is_published' not in form.changed_data:
            return super().save_model(request, obj, form, change)
        
        obj.published = timezone.now()

        return super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Tag)