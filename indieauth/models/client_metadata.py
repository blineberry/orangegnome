import socket
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
import mf2py
from requests import Response, request


class ClientMetadata():
    client_id = ""
    client_name = None
    client_uri = ""
    logo_uri = None
    redirect_uris = None

    @staticmethod
    def should_fetch(client_id):
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
        
    @staticmethod
    def from_json(json, response, client_id):
        content_client_id = json.get("client_id")

        if content_client_id is None or content_client_id != client_id:
            return None

        client = ClientMetadata()
        client.client_id = json.get(content_client_id)
        client.client_name = json.get("client_name")
        client.client_uri = json.get("client_uri")
        client.logo_uri = json.get("logo_uri")
        client.redirect_uris = []
        
        redirect_uris = json.get("redirect_uris",[])

        for uri in redirect_uris:
            client.redirect_uris.append(urljoin(response.url, uri))
        
        return client
    
    # When a client chooses to serve a web page as its client_id, the client MAY 
    # publish one or more <link> tags or Link HTTP headers with a rel attribute 
    # of redirect_uri at the client_id URL to be used by the authorization 
    # server.
    @staticmethod
    def from_html(response:Response, client_id:str):
        client = ClientMetadata()
        client.client_id = client_id
        
        try:
            content = response.content

            mf2parser = mf2py.Parser(content)

            h_apps = mf2parser.to_dict(filter_by_type="h-app")

            if len(h_apps) > 0:
                client.name = h_apps[0].get("name", [])[0]
                client.logo_uri = h_apps[0].get("logo", [])[0]
                client.client_uri = h_apps[0].get("url", [])[0]
            
            client.redirect_uris = []
        except:
            pass      

        try:
            soup = BeautifulSoup(content, 'html.parser')

            for link in soup.find_all("link", {"rel": "redirect_uri"}):
                href = link.get("href")
                if href is not None and href.strip() != '':
                    client.redirect_uris.append(urljoin(response.url, href))
        except:
            pass    

        try:   
            link_header = response.headers.get("Link")
            if link_header is None:
                return client
            
            links = link_header.split(",")
            for l in links:
                parts = l.split(";")

                for pv in parts[1:]:
                    pv_parts = pv.split("=")

                    if len(pv_parts) != 2:
                        continue

                    if pv_parts[0].strip().lower() != "rel":
                        continue

                    value = pv_parts[1].lower()
                    if value != "redirect_uri" and value != "\"redirect_uri\"":
                        continue

                    client.redirect_uris.append(parts[0].strip()[1:-1])
        except:
            pass

        return client
        
    @staticmethod
    def fetch(client_id):
        if not ClientMetadata.should_fetch(client_id):
            return None
        
        response:Response = request("GET", client_id)

        try:
            response.raise_for_status()
        except:
            return None
        
        try:
            content = response.json()
            return ClientMetadata.from_json(content, response, client_id)
        except:
            try:
                return ClientMetadata.from_html(response, client_id)
            except:
                return None