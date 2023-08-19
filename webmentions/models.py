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

class Mention:
    author = None
    permalink = None
    published = None
    content_html = None
    content_plain = None
    excerpt_html = None
    excerpt_plain = None
    title = None
    type = None

class WebmentionTypeList:
    def count(self):
        return len(self.items)
    items = []

    def __init__(self):
        self.items = []

class WebmentionList:
    def count(self):
        return len(self.webmentions)

    all = None
    replies = None
    nonreplies = None
    first_party = None

    def __init__(self, webmentions=[]):
        self.all = WebmentionTypeList()
        self.replies = WebmentionTypeList()
        self.nonreplies = WebmentionTypeList()
        self.first_party = WebmentionTypeList()

        for webmention in webmentions:
            mention = webmention.as_mention()

            self.all.items.append(mention)

            if mention.type == IncomingWebmention.BOOKMARK:
                self.nonreplies.items.append(mention)
                continue

            if mention.type == IncomingWebmention.REPLY:
                self.replies.items.append(mention)
                continue

            if webmention.is_first_party():
                self.first_party.items.append(mention)
                continue

            self.nonreplies.items.append(mention)

        
        self.all.items.sort(key = lambda x: x.published)
        self.replies.items.sort(key = lambda x: x.published)
        self.nonreplies.items.sort(key = lambda x: x.published)
        self.first_party.items.sort(key = lambda x: x.published)            

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
    
    def is_first_party(self):
        parse_result = urlparse(self.source)

        if parse_result.hostname in settings.ALLOWED_HOSTS:
            return True
        
        return False
    
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

    def is_bookmark(self):
        if "properties" not in self.h_entry:
            return False
        
        if "bookmark-of" not in self.h_entry["properties"]:
            return False
        
        for bookmark in self.h_entry["properties"]["bookmark-of"]:
            if "value" not in bookmark:
                continue
            return True
        
        return False

    def is_reply(self):
        if "properties" not in self.h_entry:
            return False
        
        if "in-reply-to" not in self.h_entry["properties"]:
            return False
        
        if self.target in self.h_entry["properties"]["in-reply-to"]:
            return True
    
        return False

    def is_like(self):
        if "properties" not in self.h_entry:
            return False
        
        if "like-of" not in self.h_entry["properties"]:
            return False
        
        for like in self.h_entry["properties"]["like-of"]:
            if like == self.target or (like.get("value") == self.target):
                return True
            
        return False

    def is_repost(self):
        if "properties" not in self.h_entry:
            return False
        
        if "repost-of" not in self.h_entry["properties"]:
            return False
        
        for repost in self.h_entry["properties"]["repost-of"]:
            if repost == self.target or (repost.get("value") == self.target):
                return True
            
        return False
    
    def get_type(self):
        if self.is_reply():
            return self.REPLY
        
        if self.is_bookmark():
            return self.BOOKMARK
        
        #if self.__try_parse_as_like():
        #    return True
        
        #if self.__try_parse_as_repost():
        #    return True
        
        return self.MENTION
            
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
    
    def __get_hentry_property_value(self, property_name, expected_type = str):        
        if self.h_entry.get("properties") is None:
            return None

        property_value = self.h_entry["properties"].get(property_name)

        if property_value is None:
            return None
        
        for value in property_value:
            if isinstance(value, expected_type):
                return value
            
            if expected_type is str and value.get("value"):
                return value["value"]
        
        return None

    def __get_published(self):
        return parse_datetime(self.__get_hentry_property_value("published"))
    
    def __get_permalink(self):
        permalink = self.__get_hentry_property_value("url")

        if permalink is not None:
            return permalink
        
        return self.source
    
    def __get_content_html(self):
        content = self.__get_hentry_property_value("content", dict)

        if content is None:
            return None
    
        if self.h_entry.get("properties") is None:
            return None
        
        html = content.get("html")

        if html is not None:
            html = bleach.clean(html, tags=bleach.sanitizer.ALLOWED_TAGS.union(('p', 'br')))
            html = bleach.linkify(html)
            t = Truncator(html)
            html = t.chars(580, "…", True)

        return html    
    
    def __get_content_plain(self):
        content = self.__get_hentry_property_value("content", str)
        
        if content is None:
            return None

        content = bleach.clean(content, tags={})
        t = Truncator(content)
        content = t.chars(580, "…", True)            

        return content
    
    def __get_excerpt_html(self):
        summary = self.__get_hentry_property_value("summary", str)

        if summary is None:
            summary = self.__get_content_html()

        if summary is None:
            return None
        
        t = Truncator(summary)
        return t.chars(240, "…", True)
    
    def __get_excerpt_plain(self):
        summary = self.__get_hentry_property_value("summary", str)

        if summary is None:
            summary = self.__get_content_html()

        if summary is None:
            return None
        
        t = Truncator(summary)
        return t.chars(240, "…", True)
    
    def __get_title(self):
        return (self.__get_hentry_property_value("name"))    
        
    def as_mention(self):
        mention = Mention()
        mention.author = self.as_author()
        mention.permalink = self.__get_permalink()
        mention.published = self.__get_published()
        mention.content_html = self.__get_content_html()
        mention.content_plain = self.__get_content_plain()
        mention.excerpt_html = self.__get_excerpt_html()
        mention.excerpt_plain = self.__get_excerpt_plain()
        mention.title = self.__get_title()
        mention.type = self.get_type()

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
        
        parsed_source = urlparse(self.source)
        parsed_target = urlparse(self.target)

        if parsed_source.netloc == parsed_target.netloc and parsed_source.path == parsed_target.path and parsed_source.params == parsed_target.params and parsed_source.query == parsed_target.query:
            result["validation_error_message"] = "Source url and Target url are the same (excluding fragment)"
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

        self.__try_get_author_from_h_entry() 
        
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

    def is_autoapproved(self):
        parsed_source = urlparse(self.source)

        return AllowedDomain.objects.filter(domain=parsed_source.netloc).exists()
    
    def autoapprove(self):
        if self.is_autoapproved():
            self.approved = True

    def add_domain_to_allowlist(self):
        parsed_source = urlparse(self.source)        
        allowed_domain = AllowedDomain.objects.get_or_create(domain=parsed_source.netloc)
        allowed_domain[0].save()

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
        self.try_parse_source_content()
        #attach
        self.try_attach_to_webmentionable()

        self.autoapprove()
    
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

class AllowedDomain(models.Model):
    domain = models.CharField(help_text="The domain from which to auto-approve webmentions.", max_length=1000)

    def __str__(self):
        return self.domain
        
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("domain",),
                name="unique_domain",
            ),
        ]