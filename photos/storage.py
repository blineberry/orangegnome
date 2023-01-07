from storages.backends.azure_storage import AzureStorage
from django.conf import settings

class PublicAzureStorage(AzureStorage):
    account_name = settings.AZURE_PUBLIC_ACCOUNT_NAME
    account_key = settings.AZURE_PUBLIC_ACCOUNT_KEY
    azure_container = settings.AZURE_PUBLIC_CONTAINER
    expiration_secs = None