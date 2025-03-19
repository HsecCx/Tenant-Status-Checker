import concurrent.futures
from utils.test_tenant_enabled import generate_oauth_token_test, load_tenants
import logging
tenants = load_tenants()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_iam_urls = {
    "US": [
        "https://iam.checkmarx.net",
        "https://us.iam.checkmarx.net"
    ],
    "EU": [
        "https://eu.iam.checkmarx.net",
        "https://eu-2.iam.checkmarx.net"
    ],
    "DEU": "https://deu.iam.checkmarx.net",
    "ANZ": "https://anz.iam.checkmarx.net",
    "IND": "https://ind.iam.checkmarx.net",
    "SNG": "https://sng.iam.checkmarx.net",
    "UAE": "https://mea.iam.checkmarx.net"
}

def get_relevant_iam_urls(regions: list | str = "US") -> list:
    """Returns the relevant IAM URLs based on the provided regions."""
    if isinstance(regions, str):
        return base_iam_urls.get(regions, [])
    elif isinstance(regions, list):
        urls = []
        for region in regions:
            if region in base_iam_urls:
                if isinstance(base_iam_urls[region], list):
                    urls.extend(base_iam_urls[region])
                else:
                    urls.append(base_iam_urls[region])
        return urls
    return []


def check_for_tenant_in_regions(tenant: str, regions: list | str = "US") -> tuple:
    """Checks if a tenant is enabled across all base URLs concurrently."""
    tenant_enabled = False
    found_url = ""
    regions = regions if isinstance(regions, list) else [regions]
    relevant_iam_urls = get_relevant_iam_urls(regions)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(generate_oauth_token_test, base_url, tenant): base_url for base_url in relevant_iam_urls}

        for future in concurrent.futures.as_completed(futures):
            base_url = futures[future]
            try:
                result = future.result()
                if ("error" and "realm") in result.lower():
                    continue  # We can assume that the tenant is not enabled.
                elif "invalid refresh token" in result.lower():
                    found_url = base_url
                    tenant_enabled = True
                    return tenant, tenant_enabled, found_url
                else:
                    raise Exception(f"Unexpected response: {result}")
            except Exception as e:
                print(f"Error checking {tenant} on {base_url}: {e}")

    return tenant, tenant_enabled, found_url

def write_data(status_list: list) -> None:
    """Writes tenant status data to a CSV file."""
    headers = ["Tenant", "Status", "Regional URL"]
    with open("tenant_status.csv", "w") as f:
        f.write(",".join(headers) + "\n")
        for status in status_list:
            f.write(f"{status[0]},{status[1]},{status[2] or 'N/A'}\n")

if __name__ == "__main__":
    tenants_status_set = set()
    MAX_THREADS = 8
    # target_regions = ["US", "EU", "DEU", "ANZ", "IND", "SNG", "UAE"]
    target_regions = ["US"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_tenant = {executor.submit(check_for_tenant_in_regions, tenant, target_regions): tenant for tenant in tenants}

        for future in concurrent.futures.as_completed(future_to_tenant):
            tenant = future_to_tenant[future]
            logging.info(f"Running, checking tenant: {tenant}")  

            try:
                result = future.result()
                tenants_status_set.add(result) 
                tenants_status_list = sorted(tenants_status_set, key=lambda x: (not x[1] ,x[0]))
            except Exception as e:
                logging.info(f"Error processing tenant {tenant}: {e}")
            logging.info(f"Finished checking tenant: {tenant}")
  
    write_data(tenants_status_list)
