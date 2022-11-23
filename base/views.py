"""
The PermalinkResponseMixin injects a `permalink` property into the view 
`context`.

The PageTitleMixin injects a `page_title` property into the view `context`.

The ForceSlugMixin redirects requests to a view with a certain PK to the URL 
with the correct slug.
"""

from django.shortcuts import redirect
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse


class PermalinkResponseMixin(TemplateResponseMixin):
    """
    Injects a `permalink` property on the `context` for any views that inherit.
    """

    canonical_viewname = ''
    """
    The viewname for the canonical view. I.e. `'notes:index'`.

    Needs to be implemented by child classes.
    """
    canonical_view_args = []
    """
    Any additional view args for the canonical view. I.e. `[self.kwargs['pk'], self.kwargs['slug']]`.

    May need to be implmented by child classes.
    """

    def get_canonical_viewname(self, context):
        """Returns the canonical_viewname from the child class."""
        return self.canonical_viewname

    def get_canonical_view_args(self, context):
        """Returns the canonical_view_args from the child class."""
        return self.canonical_view_args

    def get_context_data(self, **kwargs):
        """Returns the view context dictionary after adding a `permalink` entry."""
        context = super().get_context_data(**kwargs)
        context['permalink'] = self.request.build_absolute_uri(reverse(self.get_canonical_viewname(context), args=self.get_canonical_view_args(context)))
        return context

class PageTitleResponseMixin(TemplateResponseMixin):
    """
    Injects a `page_title` property into the view `context`.
    """
    page_title = ''
    """
    The page title for the view.

    Needs to be implemented by child classes.
    """


    def get_page_title(self, context):
        """Returns the page_title."""
        return self.page_title

    def get_context_data(self, **kwargs):
        """Returns the view context after injecting `page_title`."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title(context)

        return context

class ForceSlugMixin(TemplateResponseMixin):
    """
    Redirects requests to a view with a certain PK to the URL with the correct 
    slug.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Overrides the TemplateResponse render_to_response.

        If the request slug doesn't match the requested feed item's slug, then 
        the request is redirected to the correct URL. Prevents mischevious URL
        linking.
        """
        if context['object'].slug == self.kwargs['slug']:
            return super().render_to_response(context, **response_kwargs)
    
        return redirect(context['object'], permanent=True)