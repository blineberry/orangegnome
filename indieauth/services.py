import socket
from urllib.parse import urlsplit
from typing import TYPE_CHECKING

import requests

# if TYPE_CHECKING:
#     from indieauth.models import ClientMetadata
    
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