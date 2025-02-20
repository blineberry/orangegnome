from django.forms.widgets import Textarea, TextInput
from django.contrib.admin.widgets import AdminTextareaWidget
from django.contrib.admin.widgets import AdminTextInputWidget

class PlainTextCountTextarea(AdminTextareaWidget):
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

class PlainTextCountTextInput(AdminTextInputWidget):
    template_name = "widgets/plaintextcounttextinput.html"

    def __init__(self, attrs = None, max=""):
        super().__init__(attrs)
        self.max=max

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update({ "max": self.max })

        return context

    class Media:
        js = ["base/js/PlainTextCountTextarea.js"]