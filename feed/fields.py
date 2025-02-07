from django.db import models
from .models import convert_commonmark_to_html, convert_commonmark_to_plain_text

class CommonmarkField(models.TextField):
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
        
        html = convert_commonmark_to_html(value)

        setattr(model_instance, self.html_field, html)

        return value
        
    def _render_txt(self, value, model_instance):
        if not self.txt_field:
            return value
        
        txt = convert_commonmark_to_plain_text(value)

        setattr(model_instance, self.txt_field, txt)

        return value
    
    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)

        self._render_html(value, model_instance)
        self._render_txt(value, model_instance)

        return value
        
class CommonmarkInlineField(CommonmarkField):
    def _render_html(self, value, model_instance):
        print("CommonmarkInlineField _render_html")
        if not self.html_field:
            return value
        
        html = convert_commonmark_to_html(value, block_content=False)

        setattr(model_instance, self.html_field, html)

        return value