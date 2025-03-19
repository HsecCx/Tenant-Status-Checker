import concurrent.futures
import logging
from pathlib import Path
from utils.test_tenant_enabled import generate_oauth_token_test, load_tenants

# Configure logging format and level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load tenant data
tenants = load_tenants()

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

    # Run IAM checks concurrently for the given tenant
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

    return tenant, bool(found_urls), tuple(found_urls)  # Ensure URLs are returned as a tuple for consistency

def write_data(status_list: list[tuple], output_file_path="tenant_status.csv") -> None:
    """
    Writes tenant status data to a CSV file.

    :param status_list: A list of tuples containing tenant status data.
                        Each tuple follows (tenant, status, regional URLs).
    :param output_file_path: The file path where the CSV will be written.
                      Defaults to "tenant_status.csv".
    """
    output_file_path = Path(output_file_path).resolve()
    headers = ["Tenant", "Status", "Regional URL"]

    # Write headers and tenant status data to CSV
    with output_file_path.open("w+", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for tenant, status, urls in status_list:
            regional_url = "|".join(urls) if urls else "N/A"
            f.write(f"{tenant},{status},{regional_url}\n")

if __name__ == "__main__":
    tenants_status_set = set()
    MAX_THREADS = 8
    # target_regions = ["US", "EU", "DEU", "ANZ", "IND", "SNG", "UAE"]
    target_regions = "US"

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
                tenants_status_set.add(result)  # Add result to the set
            except Exception as e:
                logging.error(f"Error processing tenant {tenant}: {e}")

            logging.info(f"Finished checking tenant: {tenant}")

    # Write results to CSV
    write_data(sorted(tenants_status_set, key=lambda x: (not x[1], x[0])))
