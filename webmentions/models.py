from django.db import models
from django.db.models import UniqueConstraint
import requests
import re
from urllib.parse import urlsplit, urlunsplit, urljoin
from bs4 import BeautifulSoup
import html
from django.utils.encoding import punycode
from django.urls import resolve, reverse, Resolver404
from urllib.parse import (
    parse_qsl, 
    quote, unquote, urlencode, urlsplit, urlunsplit, urlparse
)
from django.utils.http import RFC3986_GENDELIMS, RFC3986_SUBDELIMS
import mf2py
from django.core.validators import URLValidator
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.apps import apps
from django.utils.dateparse import parse_datetime
import bleach
from django.utils.text import Truncator
from django.contrib import admin

class Author:
    photo = None
    name = None
    url = None

class Bookmark:
    author = None
    permalink = None
    published = None

class Reply:
    author = None
    permalink = None
    published = None
    content_html = None
    content_plain = None
    title = None

class Mention:
    author = None
    permalink = None
    published = None
    title = None

class WebmentionTypeList:
    def count(self):
        return len(self.items)
    items = []

    def __init__(self):
        self.items = []

class WebmentionList:
    def count(self):
        return len(self.webmentions)

    webmentions = []
    bookmarks = None
    replies = None
    mentions = None

    def __init__(self, webmentions=[]):
        self.webmentions = []
        self.bookmarks = WebmentionTypeList()
        self.replies = WebmentionTypeList()
        self.mentions = WebmentionTypeList()

        for mention in webmentions:
            self.webmentions.append(mention)

            if mention.type == IncomingWebmention.BOOKMARK:
                self.bookmarks.items.append(mention.as_bookmark())
                continue

            if mention.type == IncomingWebmention.REPLY:
                self.replies.items.append(mention.as_reply())
                continue

            self.mentions.items.append(mention.as_mention())

            

            

# Create your models here.
class Webmention(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    source = models.URLField(help_text="The URL that mentions the target.")
    target = models.URLField(help_text="The URL that is mentioned by the source.")

    def __str__(self):
        return self.source

    class Meta:
        abstract = True
        ordering = ["-created_at"]
    
class IncomingWebmention(Webmention):
    MENTION = "MENTION"
    REPLY = "REPLY"
    LIKE = "LIKE"
    BOOKMARK = "BOOKMARK"
    REPOST = "REPOST"
    TYPES = [
        (MENTION, "Mention"),
        (REPLY, "Reply"),
        (LIKE, "Like"),
        (BOOKMARK, "Bookmark"),
        (REPOST, "Repost")
    ]

    target = models.URLField(help_text="The URL that is mentioned by the source.")
    tries = models.PositiveSmallIntegerField(default=0)
    verified = models.BooleanField(default=False)
    source_content = models.TextField(null=True)
    source_content_type = models.CharField(null=True,max_length=50)
    type = models.CharField(max_length=8,choices=TYPES,default=MENTION)
    h_entry = models.JSONField(null=True)
    h_card = models.JSONField(null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    result = models.TextField(blank=True, default="")
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.source + " -> " + self.target
    
    def reset(self):
        self.verified = False
        self.source_content = None
        self.source_content_type = None
        self.type = self.MENTION
        self.h_entry = None
        self.h_card = None
        self.content_type = None
        self.object_id = None
        self.result = ""
        self.approved = False

    @admin.display(boolean=True,description="Fetched")
    def is_content_fetched(self):
        return self.source_content is not None

    @admin.display(boolean=True, description="Attached")
    def is_attached(self):
        return self.content_object is not None

    @admin.display(boolean=True, description="Parsed")
    def is_parsed(self):
        return self.h_entry is not None
    
    def _try_resolve_target(self):
        result = {
            "success": False,
            "resolverMatch": None
        }
        parse_result = urlparse(self.target)

        if parse_result.hostname not in settings.ALLOWED_HOSTS:
            return result
        
        try:
            result["resolverMatch"] = resolve(parse_result.path)
            result["success"] = True
            return result
        except Resolver404 as e:
            return result
        except Exception as e:
            return result
        
    def _can_target_accept_webmentions(self):
        resolve_target_result = self._try_resolve_target()
        
        if not resolve_target_result.get("success"):
            return False
        
        if not resolve_target_result.get("resolverMatch"):
            return False
        
        if not resolve_target_result["resolverMatch"].kwargs:
            return False
        
        if not resolve_target_result["resolverMatch"].kwargs.get("wm_app_name"):
            return False
        
        if not resolve_target_result["resolverMatch"].kwargs.get("wm_model_name"):
            return False
        
        if not resolve_target_result["resolverMatch"].kwargs.get("pk"):
            return False        
    
        return True
    
    def __try_get_author_from_h_entry(self):

        if "properties" not in self.h_entry:
            return False

        if "author" not in self.h_entry["properties"]:
            return False
        
        for author in self.h_entry["properties"]["author"]:
            if "h-card" not in author.get("type"):
                continue
            
            self.h_card = author
            return True                

    def __try_parse_as_bookmark(self):
        if "properties" not in self.h_entry:
            return False
        
        if "bookmark-of" not in self.h_entry["properties"]:
            return False
        
        for bookmark in self.h_entry["properties"]["bookmark-of"]:
            if "value" not in bookmark:
                continue

            self.type = self.BOOKMARK
            self.__try_get_author_from_h_entry()
            return True
        
        return False

    def __try_parse_as_reply(self):
        if "properties" not in self.h_entry:
            return False
        
        if "in-reply-to" not in self.h_entry["properties"]:
            return False
        
        if self.target in self.h_entry["properties"]["in-reply-to"]:
            self.type = self.REPLY
            self.__try_get_author_from_h_entry()
            return True
    
        return False

    def __try_parse_as_like(self):
        if "properties" not in self.h_entry:
            return False
        
        if "like-of" not in self.h_entry["properties"]:
            return False
        
        for like in self.h_entry["properties"]["like-of"]:
            if like == self.target or (like.get("value") == self.target):
                self.type = self.LIKE
                self.__try_get_author_from_h_entry()
                return True
            
        return False

    def __try_parse_as_repost(self):
        if "properties" not in self.h_entry:
            return False
        
        if "repost-of" not in self.h_entry["properties"]:
            return False
        
        for repost in self.h_entry["properties"]["repost-of"]:
            if repost == self.target or (repost.get("value") == self.target):
                self.type = self.REPOST
                self.__try_get_author_from_h_entry()
                return True
            
        return False

    def __try_parse_as_mention(self):
        if "properties" not in self.h_entry:
            return False
    
        self.__try_get_author_from_h_entry()
        return True
        
    def as_author(self):
        if not self.h_card:
            return None
        
        author = Author()

        h_card = self.h_card

        if not h_card.get("properties"):
            return None        

        author.name = h_card["properties"].get("name")
        author.photo = h_card["properties"].get("photo")
        author.url = h_card["properties"].get("url")

        if author.name is not None:
            author.name = author.name[0]

        if author.photo is not None:
            author.photo = author.photo[0]

        if author.url is not None:
            author.url = author.url[0]

        return author
        
    def as_bookmark(self):
        bookmark = Bookmark()
        bookmark.author = self.as_author()
        bookmark.permalink=self.source

        if not self.h_entry:
            return bookmark
        
        h_entry = self.h_entry
        
        if not h_entry.get("properties"):
            return bookmark
        
        bookmark.published = h_entry["properties"].get("published")
        urls = h_entry["properties"].get("url")

        if bookmark.published is not None:
            bookmark.published = parse_datetime(bookmark.published[0])

        # if the h-entry has a url, use that instead of the webmention source
        if urls is not None:
            for url in urls:
                if isinstance(url,str):
                    bookmark.permalink = url
                    break

        return bookmark
    
    def as_reply(self):
        reply = Reply()
        reply.author = self.as_author()
        reply.permalink = self.source

        if not self.h_entry:
            return reply
        
        h_entry = self.h_entry
        
        print(h_entry)

        if not h_entry.get("properties"):
            return reply
        
        reply.published = h_entry["properties"].get("published")
        urls = h_entry["properties"].get("url")
        names = h_entry["properties"].get("name")
        html = None
        plain = None
        
        if h_entry["properties"].get("content") is not None:
            html = h_entry["properties"].get("content")[0].get("html")
            plain = h_entry["properties"].get("content")[0].get("value")        

        if reply.published is not None:
            reply.published = parse_datetime(reply.published[0])

        if html is not None:
            reply.content_html = bleach.clean(html, tags=bleach.sanitizer.ALLOWED_TAGS.union(('p', 'br')))
            reply.content_html = bleach.linkify(reply.content_html)
            t = Truncator(reply.content_html)
            reply.content_html = t.chars(580, "…", True)
        
        if plain is not None:
            reply.content_plain = bleach.clean(plain, tags={})
            t = Truncator(reply.content_plain)
            reply.content_plain = t.chars(580, "…", False)

        if names is not None:
            for name in names:
                if isinstance(name, str):
                    reply.name = name

        # if the h-entry has a url, use that instead of the webmention source
        if urls is not None:
            for url in urls:
                if isinstance(url,str):
                    reply.permalink = url
                    break

        return reply
    
    def as_mention(self):
        mention = Mention()
        mention.author = self.as_author()
        mention.permalink = self.source

        if not self.h_entry:
            return mention
        
        h_entry = self.h_entry
        
        if not h_entry.get("properties"):
            return mention
        
        mention.published = h_entry["properties"].get("published")
        urls = h_entry["properties"].get("url")
        names = h_entry["properties"].get("name")

        if mention.published is not None:
            mention.published = parse_datetime(mention.published[0])

        # if the h-entry has a url, use that instead of the webmention source
        if urls is not None:
            for url in urls:
                if isinstance(url,str):
                    mention.permalink = url
                    break

        if names is not None:
            for name in names:
                if isinstance(name, str):
                    mention.name = name

        return mention
    
    def verify_request(self):
        result = {
            "success": False,
            "validation_error_message": ""
        }

        validate = URLValidator(schemes = ['http','https'])

        try:
            validate(self.source)
        except:
            result["validation_error_message"] = "Invalid source url."
            return result
        
        try:
            validate(self.target)
        except:
            result["validation_error_message"] = "Invalid source url."
            return result
        
        if self.source == self.target:
            result["validation_error_message"] = "Source url and Target url are the same."
            return result
        
        if not self._can_target_accept_webmentions():
            result["validation_error_message"] = "Target cannot accept webmentions."
            return result
        
        result['success'] = True
        return result
    
    def verify_request_and_save(self):
        result = self.verify_request()
        self.save()
        return result
    
    def try_fetch_source_content(self, force=False):
        if force:
            self.source_content = None
            self.source_content_type = None

        try:
            headers = {
                "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8"
            }
            
            source = requests.get(self.source, allow_redirects=True, headers=headers)

            self.result = str(source.status_code) + "\n\n"

            if not source.ok:
                self.result = self.result + "Fetch source content:\n\n" + self.result + " " + source.text + "\n\n"
                return False

            self.source_content = source.text
            self.source_content_type = source.headers.get('content-type')
            return True
        except Exception as e:
            self.result = self.result + "Fetch source content:\n\n" + str(e) + "\n\n"
            return False

    def try_fetch_source_content_and_save(self, force=False):
        self.try_fetch_source_content(force)
        self.save()
    
    def try_verify_webmention(self, force=False):

        if force:
            self.verified = False

        if self.source_content is None:
            self.result = str(self.result) + "Verify webmention: No source content.\n\n"
            return False

        if self.source_content_type.startswith("text/plain"):
            if self.target in self.source_content:
                self.result = str(self.result) + "Verify webmention: Target in plain text document.\n\n"
                self.verified = True
                return True
            
            self.result = str(self.result) + "Verify webmention: Plain text document does not contain target.\n\n"
            return False
        
        if self.source_content_type.startswith("application/json"):
            self.result = str(self.result) + "Verify webmention: JSON not yet supported.\n\n"
            return False

        if self.source_content_type.startswith("text/html"):
            soup = BeautifulSoup(self.source_content,features="html.parser")
            for link in soup.find_all('a'):
                if link.get('href') == self.target:
                    self.result = str(self.result) + "Verify webmention: Target in html document.\n\n"
                    self.verified = True
                    return True
                
            
            self.result = str(self.result) + "Verify webmention: target is not in source.\n\n" 
            return

        self.result = str(self.result) + "Verify webmention: Unsupported content type: " + self.source_content_type + ".\n\n"        
        return False

    def try_verify_webmention_and_save(self, force=False):
        result = self.try_verify_webmention(force)
        self.save()
        return result
    
    def try_parse_source_content(self, force=False):
        if force:
            self.h_card = None
            self.h_entry = None

        if not self.verified:
            self.result = str(self.result) + "Parse Content: Webmention is not verified.\n\n"
            return False
        
        if not self.source_content_type.startswith("text/html"):
            self.result = str(self.result) + "Parse Content: Source is not html.\n\n"
            return False
        
        o = mf2py.Parser(doc=self.source_content)
        h_entries = o.to_dict(filter_by_type="h-entry")

        if len(h_entries) > 0:
            self.h_entry = h_entries[0]

        h_cards = o.to_dict(filter_by_type="h-card")
        if len(h_cards) > 0:
            self.h_card = h_cards[0]
        
        if self.__try_parse_as_reply():
            self.result = str(self.result) + "Parse Content: Parsed as reply.\n\n"
            return True
        
        if self.__try_parse_as_bookmark():
            self.result = str(self.result) + "Parse Content: Parsed as bookmark.\n\n"
            return True
        
        #if self.__try_parse_as_like():
        #    return True
        
        #if self.__try_parse_as_repost():
        #    return True
        
        self.__try_parse_as_mention()
        self.result = self.result + "Parse Content: Parsed as mention.\n\n"
        return True
    
    def try_parse_source_content_and_save(self, force=False):
        self.try_parse_source_content(force)
        self.save()
    
    def try_attach_to_webmentionable(self, force=False):
        if force:            
            self.content_type = None
            self.object_id = None

        try:
            r = self._try_resolve_target()

            if not r.get("success"):
                self.result = self.result + "Attach: Could not resolve target.\n\n"
                return False

            resolverMatch = r.get("resolverMatch")

            if not resolverMatch:
                self.result = self.result + "Attach: No resolverMatch.\n\n"
                return False
            
            app_name = resolverMatch.kwargs.get("wm_app_name")
            model_name = resolverMatch.kwargs.get("wm_model_name")
            pk = resolverMatch.kwargs.get("pk")
            
            if not app_name or not model_name or not pk:
                self.result = self.result + "Attach: No app_name, model_name, or pk.\n\n"
                return False

            model = apps.get_model(app_name, model_name)
            webmentionable = model.objects.get(pk = pk)
            self.content_object = webmentionable
            self.result = self.result + "Attach: attached.\n\n"
            return True
        except Exception as e:
            self.result = self.result + "Attach: " + str(e) + ".\n\n"
            return False
        
    def try_attach_to_webmentionable_and_save(self, force=False):
        self.try_attach_to_webmentionable(force)
        self.save()

    def process(self, force=False):        
        self.tries += 1

        if force:
            self.reset()

        #fetch source
        if not self.try_fetch_source_content():
            return
        #verify
        if not self.try_verify_webmention():
            return
        #parse
        if not self.try_parse_source_content():
            return
        #attach
        self.try_attach_to_webmentionable()
    
    def process_and_save(self, force=False):
        try:
            self.process(force)
            self.save()
        except Exception as e:
            self.result = str(self.result) + str(e) + "\n\n"
            self.save()

    def approve(self):
        self.approved = True

    def approve_and_save(self):
        self.approve()
        self.save()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("source", "target"),
                name="unique_source_url_per_target_url_incomingwebmention",
            ),
        ]


class Webmentionable(models.Model):
    webmentions = GenericRelation(IncomingWebmention)

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        
        if self.should_send_webmentions:
            OutgoingContent.objects.get_or_create(content_url=self.get_permalink())            
        return
    
    class Meta:
        abstract = True


class OutgoingContent(models.Model):
    content_url = models.URLField(help_text="The URL with links in the content.")
    result = models.TextField(blank=True,default="")
    tries = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.content_url

    def get_source_content_mentions(self):
        result = {
            "success": True,
            "mentions": []
        }

        try:
            response = requests.get(self.content_url)

            if not response.ok:
                self.result = str(response.status_code) + " " + response.text + "\n\n"
                return result
            
            self.result = "200" + "\n\n"

            o = mf2py.Parser(doc=response.text)
            h_entry = o.to_dict(filter_by_type="h-entry")[0]

            if 'properties' not in h_entry:
                return result
            
            if 'bookmark-of' in h_entry['properties']:
                for bookmark in h_entry['properties']['bookmark-of']:
                    if "value" in bookmark:
                        result["mentions"].append(bookmark['value'])
            
            if 'in-reply-to' in h_entry['properties']:
                result["mentions"].extend(h_entry['properties']['in-reply-to'])

            if "content" not in h_entry['properties']:
                return result
            
            html = ''

            for content in h_entry['properties']['content']:
                if "html" not in content:
                    continue

                html = html + content['html']

            soup = BeautifulSoup(html, features="html.parser")
            for a in soup.find_all('a'):
                result["mentions"].append(a.get('href'))                

            return result
        
        except Exception as e: 
            self.result = str(e) + "\n\n"
            result["success"] = False
            return result
        
    def process(self):
        result = self.get_source_content_mentions()

        if not result["success"]:
            self.save()
            return

        try:
            # get existing mentions to notify them of an update
            existing_mentions = OutgoingWebmention.objects.filter(source=self.content_url)

            for mention in existing_mentions:
                mention.result = ""
                mention.success = False
                mention.tries = 0

                mention.save()

            # process the new mentions
            for mention in result["mentions"]:
                get_or_create = OutgoingWebmention.objects.get_or_create(source=self.content_url, target=mention)
                outgoing_mention = get_or_create[0]

                # if it already exists, then we should reset it because 
                # there's been an update or something and it should be reprocessed.
                if not get_or_create[1]:
                    outgoing_mention.result = ""
                    outgoing_mention.success = False
                    outgoing_mention.tries = 0

                outgoing_mention.save()

            self.delete()
        except Exception as e:
            self.result += "\n\n" + str(e)
            self.save()


        
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("content_url",),
                name="unique_content_url",
            ),
        ]

class OutgoingWebmention(Webmention):
    result = models.TextField()
    success = models.BooleanField(default=False)
    tries = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.source + " -> " + self.target
    
    def _split_header(self, header):
        return header.split(',')

    def _get_webmention_endpoint_from_header(self, linkHeader):
        links = self._split_header(linkHeader)

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

    def get_webmention_endpoint(self, url):
        response = requests.get(url, headers={
            'user-agent': 'Webmention'
        })

        url = response.url

        if 'link' in response.headers:
            link_endpoint = self._get_webmention_endpoint_from_header(response.headers['link'])
            
            if link_endpoint is not None:
                return urljoin(url, link_endpoint)

        soup = BeautifulSoup(response.text, features="html.parser")

        for el in soup.find_all(rel='webmention'):
            if el.has_attr('href'):
                return urljoin(url, el['href'])

        return None

    def try_notify_receiver(self):
        self.tries += 1
        try:
            endpoint = self.get_webmention_endpoint(self.target)
            
            if endpoint is None:
                self.result += self.result + "No webmention endpoint discovered.\n\n"
                self.success = False
                self.save()
                return self.success

            response = requests.post(endpoint, data={
                'source': self.source,
                'target': self.target,
            })

            self.result += self.result + str(response.status_code) + "\n\n"

            self.success = response.ok
            self.result += self.result + str(response.status_code) + " " + response.reason + " " + response.text + "\n\n"

            self.save()

            return self.success
        except Exception as e:
            self.result += self.result + str(e) + "\n\n"
            self.save()
            return self.success
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("source", "target"),
                name="unique_source_url_per_target_url_outgoingwebmention",
            ),
        ]
