from django.forms.widgets import Textarea

class PlainTextCountTextarea(Textarea):
    template_name = "widgets/plaintextcounttextarea.html"

    def __init__(self, attrs = None, max=""):
        super().__init__(attrs)
        self.max=max

    def get_context(self, name, value, attrs):
        context = super().get_context(name,value,attrs)
        context.update({ "max": self.max })
        return context

    class Media:
        js = ["base/js/PlainTextCountTextarea.js"]