import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class Config:
    keyVaultName = os.getenv("key_vault_name")
    EMAIL_SERVICE_URL = os.getenv("email_service_uri")
    KVUri = f"https://{keyVaultName}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)

    DB_NAME = client.get_secret("db_name")
    DB_USER = client.get_secret('db_user')
    DB_PASSWORD = client.get_secret('db_password')
    DB_URI = client.get_secret('db_uri')
    ADMIN_SECRET = client.get_secret("admin_secret")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URI}/{DB_NAME}?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '6e48ff4302924803ba0df47c2e307c78'
