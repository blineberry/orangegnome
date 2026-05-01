from django.db import models
from bs4 import BeautifulSoup
import mistune
import html2text
from django_resized import ResizedImageField
from django_resized.forms import ResizedImageFieldFile
from pillow_heif import register_heif_opener, from_pillow
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

register_heif_opener(thumbnails=False)

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

        return parser.handle(html).strip()
    
    @staticmethod
    def md_to_html(input:str, block_content:bool=True):
        if input == "":
            return ""

        conversion = mistune.html(input) #pypandoc.convert_text(input, 'html', format='commonmark+autolink_bare_uris', extra_args=["--wrap=preserve"])

        if block_content:
            return conversion.strip()

        soup = BeautifulSoup(conversion, "html.parser")

        for item in soup.find_all(CommonmarkField.block_elements):
            item.unwrap()

        return str(soup).strip()

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
        

class OGResizedImageFieldFile(ResizedImageFieldFile):
    def save(self, name, content, save=True):
        content.file.seek(0)
        img = Image.open(content.file)
        img_format = img.format.lower()

        if img_format in ('heif','mpo',):
            new_content = BytesIO()
            img_format = 'JPEG'
            img.save(new_content, format=img_format)
            content = ContentFile(new_content.getvalue())        
            name = self.get_name(name, img_format)
        
        super().save(name, content, save)

        self.field.update_dimension_fields(self.instance, force=True)

class OGResizedImageField(ResizedImageField):
    attr_class = OGResizedImageFieldFile

    def __init__(self, verbose_name=None, name=None, **kwargs):
        print(kwargs)
        super().__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        print("self")
        print(self)
        return super().check(**kwargs)