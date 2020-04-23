from django.contrib import admin
from bs4 import BeautifulSoup

# Register your models here.
class WebmentionMixin():
    def get_links_from_html(html):
        soup = BeautifulSoup(response.text, features="html.parser")


    def save_model(self, request, obj, form, change):
        links = self._get_links(obj)
        print(request)
        print(obj)
        #print(form)
        print(change)

        return super().save_model(request, obj, form, change)