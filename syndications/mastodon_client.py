from django.conf import settings
import requests


class Client(object):
    @staticmethod
    def get_auth_header():
        return 'Bearer ' + settings.MASTODON_ACCESS_TOKEN

    @staticmethod
    def get_base_url():
        return 'https://' + settings.MASTODON_INSTANCE + '/api/v1'

    @staticmethod
    def post_status(status,in_reply_to_id=None):
        data = {
            'status': status
        }

        if in_reply_to_id is not None:
            data['in_reply_to_id'] = in_reply_to_id

        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.post(Client.get_base_url() + '/statuses', data=data, headers=headers)

        response.raise_for_status()

        return response.json()

    @staticmethod
    def delete_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.delete(Client.get_base_url() + '/statuses/' + id, headers=headers)

        response.raise_for_status()

        return response.json()

