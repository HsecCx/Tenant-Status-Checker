import concurrent.futures
from utils.test_tenant_enabled import generate_oauth_token_test, load_tenants

tenants = load_tenants()

# colors = {
#     "GREEN":"\033[32m",
#     "YELLOW":"\033[33m",
#     "RED":"\033[31m",
#     "RESET":"\033[0m"
#     }

# All URLs if needed
# base_urls = [
#     "https://iam.checkmarx.net",
#     "https://us.iam.checkmarx.net",
#     "https://eu.iam.checkmarx.net",
#     "https://eu-2.iam.checkmarx.net",
#     "https://deu.iam.checkmarx.net",
#     "https://anz.iam.checkmarx.net",
#     "https://ind.iam.checkmarx.net",
#     "https://sng.iam.checkmarx.net",
#     "https://mea.iam.checkmarx.net"
# ]

# Only US.
base_urls = [
    "https://iam.checkmarx.net",
    "https://us.iam.checkmarx.net"
]

def check_for_tenant_in_all_regions(tenant: str) -> dict:
    """Checks if a tenant is enabled across all base URLs concurrently."""
    tenant_enabled = False
    found_url = ""

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all requests to be run in parallel
        futures = {executor.submit(generate_oauth_token_test, base_url, tenant): base_url for base_url in base_urls}

        for future in concurrent.futures.as_completed(futures):
            base_url = futures[future]
            try:
                result = future.result()
                if ("error" and "realm") in result.lower():
                    # We can assume that the tenant is not enabled.
                    continue
                elif "invalid refresh token" in result.lower():
                    # We can assume that the tenant is enabled.
                    found_url = base_url
                    tenant_enabled = True
                    return {"enabled": tenant_enabled, "regional_url": found_url}
                else:
                    raise Exception(f"Unexpected response: {result}")
            except Exception as e:
                print(f"Error checking {tenant} on {base_url}: {e}")

    return {"enabled": tenant_enabled, "regional_url": found_url}

def write_data(status_list: list):
    """Writes tenant status data to a CSV file."""
    headers = ["Tenant", "Status", "Regional URL"]
    with open("tenant_status.csv", "w") as f:
        f.write(",".join(headers) + "\n")
        for status in status_list:
            tenant = status["tenant"]
            enabled = status["enabled"]
            regional_url = status["regional_url"] or "N/A"
            f.write(f"{tenant},{enabled},{regional_url}\n")

if __name__ == "__main__":
    # Example for a specific tenant, this can be a string or a list. 
    # The default is all tenants in the config file.
    # MAKE SURE THE NAME IS CORRECT (case-sensitive) for specific tenants.

    tenants_status_list = []
    MAX_THREADS = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Run tenant checks in parallel
        future_to_tenant = {executor.submit(check_for_tenant_in_all_regions, tenant): tenant for tenant in tenants}

        for future in concurrent.futures.as_completed(future_to_tenant):
            tenant = future_to_tenant[future]
            print("Running, checking tenant: ", tenant)  

            try:
                result = future.result()
                # if not result["enabled"]:
                #     # We can assume that the tenant is not enabled.
                #     print(f"{colors['RED']}This tenant is not enabled (Realm not available) for {tenant}{colors['RESET']}")
                # The tenant is enabled. Refresh token is inconsequential in this for testing if the tenant is active.
                # else:
                #     print(f"{colors['GREEN']}{tenant} is enabled, on regional url: {result['regional_url']}{colors['RESET']}")
                
                tenants_status_list.append({
                    "tenant": tenant, 
                    "enabled": result["enabled"], 
                    "regional_url": result["regional_url"]
                })
                tenants_status_list = sorted(tenants_status_list, key=lambda x: (not x["enabled"], x["tenant"]))
            except Exception as e:
                print(f"Error processing tenant {tenant}: {e}")

            print("Finished checking tenant: ", tenant)
            print("\n\n")

    write_data(tenants_status_list)
