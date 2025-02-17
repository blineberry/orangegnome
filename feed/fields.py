from django.db import models
import pypandoc
from bs4 import BeautifulSoup
import os
from django.conf import settings

# Borrowed/ stolen from https://github.com/dmptrluke/django-markdownfield/tree/master

class CommonmarkField(models.TextField):
    @staticmethod
    def md_to_txt(input, strip=True):
        if input == "":
            return ""
        
        output = pypandoc.convert_text(input, os.path.join(settings.BASE_DIR, 'feed/pandocfilters/plaintext_writer.lua'), format='commonmark+raw_html', extra_args=["--wrap=preserve"])

        if not strip:
            return output
        
        return output.strip()
    
    @staticmethod
    def md_to_html(input:str, block_content:bool=True):
        if input == "":
            return ""

        conversion = pypandoc.convert_text(input, 'html', format='commonmark+autolink_bare_uris', extra_args=["--wrap=preserve"])

        if block_content:
            return conversion
        
        block_elements = ["address",
            "article",
            "aside",
            "blockquote",
            "canvas",
            "dd",
            "div",
            "dl",
            "dt",
            "fieldset",
            "figcaption",
            "figure",
            "footer",
            "form",
            "h1>-<h6",
            "header",
            "hr",
            "li",
            "main",
            "nav",
            "noscript",
            "ol",
            "p",
            "pre",
            "section",
            "table",
            "tfoot",
            "ul",
            "video"
        ]

        soup = BeautifulSoup(input, "html.parser")

        for item in soup.find_all(block_elements):
            item.unwrap()

        return str(soup)

    def __init__(self, *args, txt_field: str = None, html_field: str = None, **kwargs):
        self.txt_field = txt_field
        self.html_field = html_field

        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.txt_field is not None:
            kwargs['txt_field'] = self.txt_field

        if self.html_field is not None:
            kwargs['html_field'] = self.html_field

        return name, path, args, kwargs
    
    def _render_html(self, value, model_instance):
        if not self.html_field:
            return value
        
        html = CommonmarkField.md_to_html(value)

        setattr(model_instance, self.html_field, html)

        return value
        
    def _render_txt(self, value, model_instance):
        if not self.txt_field:
            return value
        
        txt = CommonmarkField.md_to_txt(value)

        setattr(model_instance, self.txt_field, txt)

        return value
    
    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)

        self._render_html(value, model_instance)
        self._render_txt(value, model_instance)

        return value
        
class CommonmarkInlineField(CommonmarkField):
    @staticmethod
    def md_to_html(input:str, block_content:bool=True):
        return CommonmarkField(input,block_content)

    def _render_html(self, value, model_instance):
        if not self.html_field:
            return value
        
        html = CommonmarkField.md_to_html(value, block_content=False)

        setattr(model_instance, self.html_field, html)

        return value