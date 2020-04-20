from django.shortcuts import render
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse

# Create your views here.
class PermalinkResponseMixin(TemplateResponseMixin):
    canonical_viewname = ''
    canonical_view_args = []

    def get_canonical_viewname(self, context):
        return self.canonical_viewname

    def get_canonical_view_args(self, context):
        return self.canonical_view_args

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permalink'] = self.request.build_absolute_uri(reverse(self.get_canonical_viewname(context), args=self.get_canonical_view_args(context)))
        return context

class PageTitleResponseMixin(TemplateResponseMixin):
    page_title = ''

    def get_page_title(self, context):
        return title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title(context)

        return context

class ForceSlugMixin(TemplateResponseMixin):
    def render_to_response(self, context, **response_kwargs):
        if context['object'].slug == self.kwargs['slug']:
            return super().render_to_response(context, **response_kwargs)
    
        return redirect(context['object'], permanent=True)