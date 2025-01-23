from django.forms.widgets import Textarea, Widget

class PlainTextCountTextarea(Textarea):
    template_name = "widgets/plaintextcounttextarea.html"

    def __init__(self, attrs = None, max=""):
        super().__init__(attrs)
        self.max=max

    def get_context(self, name, value, attrs):
        context = super().get_context(name,value,attrs)
        context.update({ "max": self.max })
        print(context)
        return context
    
    def render(self, name, value, attrs=None, renderer=None):
        r = super().render(name, value, attrs, renderer)
        print(r)
        return r

    class Media:
        js = ["base/js/PlainTextCountTextarea.js"]