from django.contrib import admin
from bs4 import BeautifulSoup
from .models import Webmention

# Register your models here.
class WebmentionMixin():
    send_webmentions = True
    links_to_webmention = []

    def get_links_to_webmention(self, request, obj, form, change):
        return self.links_to_webmention

    def send_webmentions(self, request, obj, form, change):
        if not self.should_send_webmentions(request,obj,form,change):   
            return
        
        links = self.links_to_webmention

        for link in links:
            Webmention.send(obj.get_permalink(), link)
            print("send webmention for " + link)

    def should_send_webmentions(self, request, obj, form, change):
        return self.send_webmentions

class WebmentionAdmin(WebmentionMixin, admin.ModelAdmin):
    def save_model(self, request, obj, form, change):    
        self.links_to_webmention = self.get_links_to_webmention(request, obj, form, change)

        saveresponse = super().save_model(request, obj, form, change)

        self.send_webmentions(request, obj, form, change)
        
        return saveresponse