import socket
from urllib.parse import urlsplit

import requests

from indieauth.models import ClientMetadata

def should_fetch_client_id(client_id):
    try:
        split = urlsplit(client_id)
        unauthorized_netloc = [
            '127.0.0.0', 
            '127.0.0.1', 
            '127.0.0.2'
            '127.0.0.3'
            '127.0.0.4'
            '127.0.0.5'
            '127.0.0.6'
            '127.0.0.7'
            '127.0.0.8'
            '[::1]']

        if split.netloc in unauthorized_netloc:
            return False
        
        addrinfo = socket.getaddrinfo(split.netloc, None, socket.AF_UNSPEC)

        for i in addrinfo:
            for ip in i[4]:
                if ip in unauthorized_netloc:
                    return False
                
        return True
        
    except:
        return False

def get_client_metadata(client_id):
    if not should_fetch_client_id(client_id):
        return None
    
def canonicalize_url(url):
    split = urlsplit(url)

    path = split.path
    netloc = split.netloc.lower()

    if path == '':
        path = '/'

    url = f'{split.scheme}://{netloc}{path}'

    if split.query != '':
        url += f'?{split.query}'

    if split.fragment != '':
        url += f'#{split.fragment}'

    return url