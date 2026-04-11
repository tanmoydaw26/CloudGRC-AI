"""
Azure Connector — authenticates via Service Principal using env variables.
Uses azure-identity and azure-mgmt SDKs.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def get_azure_credential():
    """Return Azure ClientSecretCredential."""
    from azure.identity import ClientSecretCredential
    tenant = os.getenv("AZURE_TENANT_ID")
    client = os.getenv("AZURE_CLIENT_ID")
    secret = os.getenv("AZURE_CLIENT_SECRET")
    if not all([tenant, client, secret]):
        raise RuntimeError("[Azure] Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET.")
    cred = ClientSecretCredential(tenant_id=tenant, client_id=client, client_secret=secret)
    print("[Azure] Credential object created.")
    return cred

def get_subscription_id() -> str:
    sub = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not sub:
        raise RuntimeError("[Azure] Set AZURE_SUBSCRIPTION_ID env var.")
    return sub

def get_storage_client():
    from azure.mgmt.storage import StorageManagementClient
    return StorageManagementClient(get_azure_credential(), get_subscription_id())

def get_network_client():
    from azure.mgmt.network import NetworkManagementClient
    return NetworkManagementClient(get_azure_credential(), get_subscription_id())

def get_monitor_client():
    from azure.mgmt.monitor import MonitorManagementClient
    return MonitorManagementClient(get_azure_credential(), get_subscription_id())

def get_auth_client():
    from azure.mgmt.authorization import AuthorizationManagementClient
    return AuthorizationManagementClient(get_azure_credential(), get_subscription_id())
