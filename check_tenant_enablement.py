import concurrent.futures
import logging
import argparse
from pathlib import Path
import requests


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

# Configure logging format and level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Mapping of IAM base URLs by region
base_iam_urls = {
    "US": ["https://iam.checkmarx.net", "https://us.iam.checkmarx.net"],
    "EU": ["https://eu.iam.checkmarx.net", "https://eu-2.iam.checkmarx.net"],
    "DEU": ["https://deu.iam.checkmarx.net"],
    "ANZ": ["https://anz.iam.checkmarx.net"],
    "IND": ["https://ind.iam.checkmarx.net"],
    "SNG": ["https://sng.iam.checkmarx.net"],
    "UAE": ["https://mea.iam.checkmarx.net"],
}

colors = {
     "GREEN":"\033[32m",
     "YELLOW":"\033[33m",
     "RED":"\033[31m",
     "RESET":"\033[0m"
     }
 

def get_relevant_iam_urls(regions: list | str = "US") -> list:
    """
    Returns a list of IAM URLs based on the provided regions.

    :param regions: A single region (str) or a list of regions (list of str).
                    Defaults to "US".
    :return: A list of IAM base URLs for the specified regions.
    """
    return sum((base_iam_urls.get(region, []) for region in ([regions] if isinstance(regions, str) else regions)), [])

def check_for_tenant_in_regions(tenant: str, regions: list | str = "US", multi_region_output: bool = False) -> tuple:
    """
    Checks if a tenant is enabled across target IAM base URLs concurrently.

    :param tenant: The tenant name to check.
    :param regions: A single region (str) or a list of regions (list of str).
                    Defaults to "US".
    :param multi_region_output: If True, returns all matching URLs; otherwise,
                                returns the first found URL.
    :return: A tuple (tenant, bool indicating if enabled, tuple of matching URLs).
    """
    relevant_iam_urls = get_relevant_iam_urls(regions)
    found_urls = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(generate_oauth_token_test, url, tenant): url for url in relevant_iam_urls}

        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                result = future.result().lower()
                if "error" in result and "realm" in result:
                    continue  # Tenant is not enabled
                if "invalid refresh token" in result:
                    found_urls.append(url)
                    if not multi_region_output:
                        return tenant, True, url  # Return early if not checking multiple regions
            except Exception as e:
                logging.error(f"Error checking {tenant} on {url}: {e}")

    return tenant, bool(found_urls), tuple(found_urls)

def write_data(status_list: list, file_path="tenant_status.csv") -> None:
    """
    Writes tenant status data to a CSV file.

    :param status_list: A list of tuples containing tenant status data.
                        Each tuple follows (tenant, status, regional URLs).
    :param file_path: The file path where the CSV will be written.
                      Defaults to "tenant_status.csv".
    """
    file_path = Path(file_path).resolve()
    headers = ["Tenant", "Status", "Regional URL"]

    with file_path.open("w+", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for tenant, status, urls in status_list:
            regional_url = "|".join(urls) if urls else "N/A"
            f.write(f"{tenant},{status},{regional_url}\n")

def parse_arguments():
    """
    Parses command-line arguments for tenant filtering.
    
    :return: List of tenant names provided via command-line, or an empty list if none.
    """
    parser = argparse.ArgumentParser(description="Check if tenants are enabled in different IAM regions.")
    parser.add_argument(
        "--tenants", nargs="+", help="List of tenant names to check (space-separated)."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Load all tenants unless specific ones are provided via arguments
    tenants = args.tenants if args.tenants else load_tenants()

    tenants_status_set = set()
    MAX_THREADS = 8
    target_regions = ["US", "EU", "DEU", "ANZ", "IND", "SNG", "UAE"]

    # Execute IAM checks concurrently for all tenants
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_tenant = {
            executor.submit(check_for_tenant_in_regions, tenant, target_regions, True): tenant
            for tenant in tenants
        }

        for future in concurrent.futures.as_completed(future_to_tenant):
            tenant = future_to_tenant[future]
            logging.info(f"Checking tenant: {tenant}")

            try:
                result = future.result()
                tenants_status_set.add(result)
            except Exception as e:
                logging.error(f"Error processing tenant {tenant}: {e}")

            logging.info(f"Finished checking tenant: {tenant}")

    # Sort results before writing
    tenants_status_list = sorted(tenants_status_set, key=lambda x: (not x[1], x[0]))

    # Write results to CSV
    write_data(tenants_status_list)

    # Print results to console
    if args.tenants:
        print("\n--- Tenant Check Results ---")
        for tenant, status, urls in tenants_status_list:
            status_str = "Enabled" if status else "Disabled"
            regional_url = "|".join(urls) if urls else "N/A"
            if status_str == "Enabled":
                print(f"{colors['GREEN']}Tenant: {tenant}, Status: {status_str}, Regional URL(s): {regional_url}{colors['RESET']}")
            else:
                print(f"{colors['RED']}Tenant: {tenant}, Status: {status_str}, Regional URL(s): {regional_url}{colors['RESET']}")
