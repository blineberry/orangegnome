from django.db import models
import requests
import re
from urllib.parse import urlsplit, urlunsplit, urljoin
from bs4 import BeautifulSoup

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
        webmention_endpoint = Webmention.get_webmention_endpoint(targetUrl)

        if webmention_endpoint is None:
            return False

        return Webmention.notify_receiver(sourceUrl, targetUrl, webmention_endpoint)
        

               