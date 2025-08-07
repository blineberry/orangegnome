import re
from django.db import models
import pypandoc
from bs4 import BeautifulSoup, Comment, NavigableString
import os
from django.conf import settings
from mf2py.dom_helpers import get_textContent
import mistune
from mistune.renderers.markdown import MarkdownRenderer
from typing import cast
import html2text

class PlainTextRenderer(MarkdownRenderer):
    def link(self, token, state):
        text = self.render_children(token, state)
        out = text

        attrs = token["attrs"]
        url = attrs["url"]

        if text == url:
            return text
        elif "mailto:" + text == url:
            return text
        
        return out + " (" + url + ")"
    
    def image(self, token, state):

        alt = self.render_children(token, state)

        if alt is not None:
            return " " + alt + " "
        
        attrs = token["attrs"]
        print(str(attrs))
        src = attrs.get("url")

        if src is not None:
            return " " + src + " "

        return ""

_whitespace_to_space_regex = re.compile(r"[\n\t\r]+")
_reduce_spaces_regex = re.compile(r" {2,}")

class CommonmarkField(models.TextField):   
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
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
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

    @staticmethod
    def md_to_txt(input, strip=True):
        if input == "":
            return ""
        
        html = CommonmarkField.md_to_html(input)
        soup = BeautifulSoup(CommonmarkField.md_to_html(input), "html.parser")
        for el in soup.find_all(["script", "style", "template"]):
            el.decompose()

        for el in soup.find_all("img"):
            alt = el.get("alt")
            if alt is not None:
                el.replace_with(" " + alt + " ")
                continue
            
            src = el.get("src")
            if src is not None:
                el.replace_with(" " + src + " ")
                continue
            
            el.decompose()

        for el in soup.find_all("a"):
            href = el.get("href")
            text = el.get_text()

            if href is not None and href != text:
                el.append(" (" + href + ")")

            el.unwrap()

        for el in soup.find_all(["h1","h2","h3","h4","h5","h6"]):
            el.name = "p"

        html = str(soup)

        parser = html2text.HTML2Text()
        parser.strong_mark = "*"
        parser.unicode_snob = True
        parser.body_width = 0
        parser.wrap_links = True
        parser.images_to_alt = True
        parser.ul_item_mark = "-"

        return parser.handle(html)
    
    @staticmethod
    def md_to_html(input:str, block_content:bool=True):
        if input == "":
            return ""

        conversion = mistune.html(input) #pypandoc.convert_text(input, 'html', format='commonmark+autolink_bare_uris', extra_args=["--wrap=preserve"])

        if block_content:
            return conversion

        soup = BeautifulSoup(conversion, "html.parser")

        for item in soup.find_all(CommonmarkField.block_elements):
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
    def md_to_html(input:str, block_content:bool=False):
        return CommonmarkField.md_to_html(input,block_content)

    def _render_html(self, value, model_instance):
        if not self.html_field:
            return value
        
        html = CommonmarkField.md_to_html(value, block_content=False)

        setattr(model_instance, self.html_field, html)

        return value