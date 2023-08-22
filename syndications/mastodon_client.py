from django.conf import settings
import requests


class Client(object):
    @staticmethod
    def get_auth_header():
        return 'Bearer ' + settings.MASTODON_ACCESS_TOKEN

    @staticmethod
    def get_base_url():
        return 'https://' + settings.MASTODON_INSTANCE + '/api'

    @staticmethod
    def get_v1_url():
        return Client.get_base_url() + '/v1'

    @staticmethod
    def get_v2_url():
        return Client.get_base_url() + '/v2'

    @staticmethod
    def post_status(status, idempotency_key, in_reply_to_id=None, media_ids=None, visibility='public'):
        data = {
            'status': status,
            'visibility': visibility
        }

        if in_reply_to_id is not None:
            data['in_reply_to_id'] = in_reply_to_id

        if media_ids is not None:
            data['media_ids[]'] = media_ids

        headers = {
            'Authorization': Client.get_auth_header()
            #'Idempotency-Key': idempotency_key # need to figure out how to use a value for this that updates after model saves.
        }

        response = requests.post(Client.get_v1_url() + '/statuses', data=data, headers=headers)

        response.raise_for_status()

        return response.json()

    @staticmethod
    def delete_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.delete(Client.get_v1_url() + '/statuses/' + id, headers=headers)

        response.raise_for_status()

        return response.json()

    @staticmethod
    def post_media(file, thumbnail=None, description=None, focus=None):
        """
        Sends a Upload media as an attachment (async) request.
        https://docs.joinmastodon.org/methods/media/#v2

        file: required. Object. The file to be attached, encoded using 
            multipart form data. The file must have a MIME type.

        thumbnail: Object. The custom thumbnail of the media to be 
            attached, encoded using multipart form data.

        description: String. A plain-text description of the media, for 
            accessibility purposes.
    
        focus: String. Two floating points (x,y), comma-delimited, ranging 
            from -1.0 to 1.0. See Focal points for cropping media 
            thumbnails for more information.

        """
        files = {
            'file': file
        }

        data = {}

        if thumbnail is not None:
            data['thumbnail'] = thumbnail
        
        if description is not None:
            data['description'] = description

        if focus is not None:
            data['focus'] = focus

        headers = {
            'Authorization': Client.get_auth_header(),
        }

        response = requests.post(Client.get_v2_url() + '/media', files=files, data=data, headers=headers)

        response.raise_for_status()

        return response.json()
    
    @staticmethod
    def favorite_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.post(Client.get_v1_url() + '/statuses/' + id + "/favourite", headers=headers)

        response.raise_for_status()

        return response.json()
    
    @staticmethod
    def unfavorite_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.post(Client.get_v1_url() + '/statuses/' + id + "/unfavourite", headers=headers)

        response.raise_for_status()

        return response.json()
    
    @staticmethod
    def boost_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.post(Client.get_v1_url() + '/statuses/' + id + "/reblog", headers=headers)

        response.raise_for_status()

        return response.json()
    
    @staticmethod
    def unboost_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.post(Client.get_v1_url() + '/statuses/' + id + "/unreblog", headers=headers)

        response.raise_for_status()

        return response.json()