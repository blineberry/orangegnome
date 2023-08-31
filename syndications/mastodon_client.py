from django.conf import settings
import requests
from mastodon import Mastodon


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
    def get_status(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.get(Client.get_v1_url() + '/statuses/' + id, headers=headers)

        response.raise_for_status()

        return response.json()

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
    def get_status_context(id):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        response = requests.get(Client.get_v1_url() + '/statuses/' + id + "/context", headers=headers)

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
    
    @staticmethod
    def get_status_boost_accounts(id, limit=40, endpoint=None, return_json=True):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        params = {}

        for key in ["limit"]:
            value = eval(key)
            
            if value is not None:
                params[key] = value

        if endpoint is None:
            endpoint = Client.get_v1_url() + '/statuses/' + id + "/reblogged_by"

        response = requests.get(endpoint, headers=headers, params=params)

        response.raise_for_status()

        if return_json:
            return response.json()
        
        return response
    
    @staticmethod
    def get_status_boost_accounts_all(id):
        all_accounts = []
        endpoint = None
        end = False

        while end is False:
            response = None
            
            if endpoint is None:
                response = Client.get_status_boost_accounts(id, limit=80, return_json=False)
            else:
                response = Client.get_status_boost_accounts(id, endpoint=endpoint, return_json=False)

            if response is None:
                end = True
                break

            if not response.ok:
                end = True
                break

            accounts = response.json()

            if len(accounts) <= 0:
                end = True
                break

            all_accounts.extend(response.json())

            if not response.links.get("next"):
                end = True
                break
            
            endpoint = response.links.get("next").get("url")

        return all_accounts

    
    @staticmethod
    def get_status_favorite_accounts(id, limit=40, endpoint=None, return_json=True):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        params = {}

        for key in ["limit"]:
            value = eval(key)
            
            if value is not None:
                params[key] = value

        if endpoint is None:
            endpoint = Client.get_v1_url() + '/statuses/' + id + "/favourited_by"

        response = requests.get(endpoint, headers=headers, params=params)

        response.raise_for_status()

        if return_json:
            return response.json()
        
        return response
    
    @staticmethod
    def get_status_favorite_accounts_all(id):
        all_accounts = []
        endpoint = None
        end = False

        while end is False:
            response = None
            
            if endpoint is None:
                response = Client.get_status_favorite_accounts(id, limit=80, return_json=False)
            else:
                response = Client.get_status_favorite_accounts(id, endpoint=endpoint, return_json=False)

            if response is None:
                end = True
                break

            if not response.ok:
                end = True
                break

            accounts = response.json()

            if len(accounts) <= 0:
                end = True
                break

            all_accounts.extend(response.json())

            if not response.links.get("next"):
                end = True
                break
            
            endpoint = response.links.get("next").get("url")

        return all_accounts
    
    @staticmethod
    def get_account_statuses(id,max_id=None,since_id=None,min_id=None,limit=20,only_media="false",exclude_replies="false",exclude_reblogs="false",pinned="false",tagged=None,endpoint=None, return_json=True):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        params = {}

        for key in ["max_id","since_id","min_id","limit","only_media","exclude_replies","exclude_reblogs","pinned","tagged"]:
            value = eval(key)
            
            if value is not None:
                params[key] = value

        if endpoint is None:
            endpoint = Client.get_v1_url() + '/accounts/' + id + "/statuses"

        response = requests.get(endpoint, headers=headers, params=params)

        response.raise_for_status()

        if return_json:
            return response.json()
        
        return response
    
    @staticmethod
    def get_account_status_by_reblog_of_id(reblog_of_id, account_id):
        reblog_status = None
        endpoint = None
        end = False

        while reblog_status is None and end is False:
            response = None

            if endpoint is None:
                response = Client.get_account_statuses(account_id,max_id=reblog_of_id,return_json=False,exclude_replies="true")
            else:
                response = Client.get_account_statuses(account_id,endpoint=endpoint,return_json=False)

            if response is None:
                end = True
                break

            if not response.ok:
                    end = True
                    break
            
            statuses = response.json()

            if len(statuses) == 0:
                end = True
                break

            for status in statuses:
                if status.get("reblog") is None:
                    continue
                if status.get("reblog").get("id") != reblog_of_id:
                    continue

                reblog_status = status
                break

            if not response.links.get("prev"):
                end = True
                break
            
            endpoint = response.links.get("prev").get("url")

        return reblog_status

    @staticmethod
    def push_subscription_subscribe(
        subscription_endpoint,
        subscription_keys_p256dh,
        subscription_keys_auth,
        data_alerts_mention=False,
        data_alerts_status=False,
        data_alerts_reblog=False,
        data_alerts_follow=False,
        data_alerts_follow_request=False,
        data_alerts_favourite=False,
        data_alerts_poll=False,
        data_alerts_update=False,
        data_alerts_admin_sign_up=False,
        data_alerts_admin_report=False,
        data_policy="none"
    ):
        headers = {
            'Authorization': Client.get_auth_header()
        }

        data = {
            "subscription": {
                "endpoint": subscription_endpoint,
                "keys": {
                    "p256dh": subscription_keys_p256dh,
                    "auth": subscription_keys_auth
                }
            },
            "data": {
                "alerts": {
                    "mention": data_alerts_mention,
                    "status": data_alerts_status,
                    "reblog": data_alerts_reblog,
                    "follow": data_alerts_follow,
                    "follow_request": data_alerts_follow_request,
                    "favourite": data_alerts_favourite,
                    "poll": data_alerts_poll,
                    "update": data_alerts_update,
                    "admin.signup": data_alerts_admin_sign_up,
                    "admin.report": data_alerts_admin_report
                },
                "policy": data_policy
            }            
        }

        response = requests.post(Client.get_v1_url() + '/push/subscription', headers=headers, data=data)

        response.raise_for_status()

        return response.json()
    
    @staticmethod
    def push_subscription_generate_keys():
        mastodon = Mastodon(access_token=settings.MASTODON_ACCESS_TOKEN, api_base_url='https://' + settings.MASTODON_INSTANCE)

        return mastodon.push_subscription_generate_keys()

    @staticmethod
    def push_subscription_set(endpoint,encrypt_params):
        mastodon = Mastodon(access_token=settings.MASTODON_ACCESS_TOKEN, api_base_url='https://' + settings.MASTODON_INSTANCE)

        #print(keys)
        #print(keys[1])

        #json_object = json.dumps(keys)
        #print(json_object)
        #json_dict = json.loads(json_object)
        #print(json_dict)

        response = mastodon.push_subscription_set(
            endpoint=endpoint, 
            encrypt_params=encrypt_params,
            favourite_events=1,
            reblog_events=1)

        print(response)

        return response

        #return MastodonPushSubscription.objects.update_or_create()

    @staticmethod
    def push_subscription_decrypt_push(data, decrypt_params, encryption_header, crypto_key_header):
        mastodon = Mastodon(access_token=settings.MASTODON_ACCESS_TOKEN, api_base_url='https://' + settings.MASTODON_INSTANCE)

        return mastodon.push_subscription_decrypt_push(data=data, decrypt_params=decrypt_params,encryption_header=encryption_header,crypto_key_header=crypto_key_header)



                


