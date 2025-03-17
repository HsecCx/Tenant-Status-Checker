import concurrent.futures
from utils.test_tenant_enabled import generate_oauth_token_test, load_tenants

tenants = load_tenants()

# Only US.
base_urls = [
    "https://iam.checkmarx.net",
    "https://us.iam.checkmarx.net"
]

def check_for_tenant_in_all_regions(tenant: str) -> tuple:
    """Checks if a tenant is enabled across all base URLs concurrently."""
    tenant_enabled = False
    found_url = ""

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(generate_oauth_token_test, base_url, tenant): base_url for base_url in base_urls}

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_tenant = {executor.submit(check_for_tenant_in_all_regions, tenant): tenant for tenant in tenants}

        for future in concurrent.futures.as_completed(future_to_tenant):
            tenant = future_to_tenant[future]
            print("Running, checking tenant: ", tenant)  

            try:
                result = future.result()
                tenants_status_set.add(result)  # Set ensures uniqueness

                # Correct sorting of tuples
                tenants_status_list = sorted(tenants_status_set, key=lambda x: (not x[1] ,x[0]))
            except Exception as e:
                print(f"Error processing tenant {tenant}: {e}")

            print("Finished checking tenant: ", tenant)
            print("\n\n")

    # Convert tuples to dictionaries before writing to file
    write_data(tenants_status_list)
