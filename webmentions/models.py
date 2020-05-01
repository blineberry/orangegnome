from django.db import models
import requests
import re
from urllib.parse import urlsplit, urlunsplit, urljoin
from bs4 import BeautifulSoup
import html
from django.utils.encoding import punycode
from urllib.parse import (
    #parse_qsl, 
    quote, unquote, #urlencode, urlsplit, urlunsplit,
)
from django.utils.http import RFC3986_GENDELIMS, RFC3986_SUBDELIMS

# Create your models here.
class Webmention():
    @staticmethod
    def _split_header(header):
        return header.split(',')

    @staticmethod
    def _get_webmention_endpoint_from_header(linkHeader):
        links = Webmention._split_header(linkHeader)

        for link in links:
            linkParts = link.split(';')

            if (len(linkParts) < 2):
                continue

            if re.search("rel=\"?(.* )?webmention(.* )?\"?", linkParts[1].strip()) is not None:
                matches = re.match("<(.+)>", linkParts[0].strip())

                if matches is None:
                    continue

                return matches.groups()[0]

        return None

    # Heavily taken from https://github.com/django/django/blob/master/django/utils/html.py#L236
    @staticmethod
    def get_links_from_text(text):
        WRAPPING_PUNCTUATION = [('(', ')'), ('[', ']')]
        TRAILING_PUNCTUATION_CHARS = '.,:;!'

        def smart_urlquote(url):
            """Quote a URL if it isn't already quoted."""
            def unquote_quote(segment):
                segment = unquote(segment)
                # Tilde is part of RFC3986 Unreserved Characters
                # https://tools.ietf.org/html/rfc3986#section-2.3
                # See also https://bugs.python.org/issue16285
                return quote(segment, safe=RFC3986_SUBDELIMS + RFC3986_GENDELIMS + '~')

            # Handle IDN before quoting.
            try:
                scheme, netloc, path, query, fragment = urlsplit(url)
            except ValueError:
                # invalid IPv6 URL (normally square brackets in hostname part).
                return unquote_quote(url)

            try:
                netloc = punycode(netloc)  # IDN -> ACE
            except UnicodeError:  # invalid domain part
                return unquote_quote(url)

            if query:
                # Separately unquoting key/value, so as to not mix querystring separators
                # included in query values. See #22267.
                query_parts = [(unquote(q[0]), unquote(q[1]))
                            for q in parse_qsl(query, keep_blank_values=True)]
                # urlencode will take care of quoting
                query = urlencode(query_parts)

            path = unquote_quote(path)
            fragment = unquote_quote(fragment)

            return urlunsplit((scheme, netloc, path, query, fragment))

        def trim_punctuation(lead, middle, trail):
            """
            Trim trailing and wrapping punctuation from `middle`. Return the items
            of the new state.
            """
            # Continue trimming until middle remains unchanged.
            trimmed_something = True
            while trimmed_something:
                trimmed_something = False
                # Trim wrapping punctuation.
                for opening, closing in WRAPPING_PUNCTUATION:
                    if middle.startswith(opening):
                        middle = middle[len(opening):]
                        lead += opening
                        trimmed_something = True
                    # Keep parentheses at the end only if they're balanced.
                    if (middle.endswith(closing) and
                            middle.count(closing) == middle.count(opening) + 1):
                        middle = middle[:-len(closing)]
                        trail = closing + trail
                        trimmed_something = True
                # Trim trailing punctuation (after trimming wrapping punctuation,
                # as encoded entities contain ';'). Unescape entities to avoid
                # breaking them by removing ';'.
                middle_unescaped = html.unescape(middle)
                stripped = middle_unescaped.rstrip(TRAILING_PUNCTUATION_CHARS)
                if middle_unescaped != stripped:
                    trail = middle[len(stripped):] + trail
                    middle = middle[:len(stripped) - len(middle_unescaped)]
                    trimmed_something = True
            return lead, middle, trail

        word_split_re = r'''([\s<>"']+)'''
        simple_url_re = r'^https?://\[?\w'
        simple_url_2_re = r'^www\.|^(?!http)\w[^@]+\.(com|edu|gov|int|mil|net|org)($|/.*)$'

        words = re.split(word_split_re, text)

        urls = list()
        for i, word in enumerate(words):
            if '.' in word or '@' in word or ':' in word:
                lead, middle, trail = '', word, ''
                lead, middle, trail = trim_punctuation(lead, middle, trail)
                
                url = None
                if re.match(simple_url_re, middle):
                    urls.append(smart_urlquote(html.unescape(middle)))
                    continue            
                
                if re.match(simple_url_2_re, middle, re.IGNORECASE):
                    urls.append(smart_urlquote('http://%s' % html.unescape(middle)))
                    continue

        return urls

    @staticmethod
    def get_links_from_html(html):
        soup = BeautifulSoup(html, features="html.parser")
        href_els = soup.find_all(href=re.compile(".+"))

        if len(href_els) < 1:
            return list()

        return [e['href'] for e in href_els]

    @staticmethod
    def get_webmention_endpoint(url):
        response = requests.get(url, headers={
            'user-agent': 'Webmention'
        })

        url = response.url

        if 'link' in response.headers:
            link_endpoint = Webmention._get_webmention_endpoint_from_header(response.headers['link'])
            
            if link_endpoint is not None:
                return urljoin(url, link_endpoint)

        soup = BeautifulSoup(response.text, features="html.parser")

        for el in soup.find_all(rel='webmention'):
            if el.has_attr('href'):
                return urljoin(url, el['href'])

        return None

    @staticmethod
    def notify_receiver(source, target, webmention_endpoint):
        response = requests.post(webmention_endpoint, data={
            'source': source,
            'target': target,
        })

        return response.status_code >= 200 and response.status_code < 300

    @staticmethod
    def send(sourceUrl, targetUrl):
        print(f'Sending webmention notification to { targetUrl } for { sourceUrl }')

        webmention_endpoint = Webmention.get_webmention_endpoint(targetUrl)

        if webmention_endpoint is None:
            return False

        if Webmention.notify_receiver(sourceUrl, targetUrl, webmention_endpoint):
            print(f'webmention notification sent to { targetUrl } for { sourceUrl }')
            return True

        return False