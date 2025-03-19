import requests,json
from pathlib import Path

def load_tenants(tenants_file=Path("tenants.txt").resolve()) -> list:
    with open(tenants_file, "r") as file:
        return list(dict.fromkeys(file.read().splitlines()))
    
def generate_oauth_token_test(iam_url: str, tenant: str) -> str:
    """
    Generates an OAuth token using the provided API key.

    Parameters:
        config (dict): Configuration dictionary with IAM URL, API key, and tenant name.

    Returns:
        str: The OAuth token if successful, or an error message if not.
    """
    url = f"{iam_url}/auth/realms/{tenant}/protocol/openid-connect/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": "ast-app",
        "refresh_token": " "
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token", "Error: Access token not found.")
    return f"Error: Failed to generate token. Status: {response.status_code}, Response: {response.text}"