from utils.test_tenant_enabled import generate_oauth_token_test,load_tenants

tenants = load_tenants()
colors = {
    "GREEN":"\033[32m",
    "YELLOW":"\033[33m",
    "RED":"\033[31m",
    "RESET":"\033[0m"
    }
base_urls = [
    "https://iam.checkmarx.net",
    "https://us.iam.checkmarx.net",
    "https://eu.iam.checkmarx.net",
    "https://eu-2.iam.checkmarx.net",
    "https://deu.iam.checkmarx.net",
    "https://anz.iam.checkmarx.net",
    "https://ind.iam.checkmarx.net",
    "https://sng.iam.checkmarx.net",
    "https://mea.iam.checkmarx.net"
]

def check_for_tenant_in_all_regtions(tenant: str) -> dict:
    tenant_enabled = False
    found_url = ""
    for base_url in base_urls:
        result = generate_oauth_token_test(base_url, tenant)
        if ("error" and "realm") in result.lower():
            #We can assume that the tenant is not enabled.
            continue
        elif "invalid refresh token" in result.lower():
            #We can assume that the tenant is enabled.
            found_url = base_url
            tenant_enabled = True
            return {"enabled":tenant_enabled, "regional_url":found_url}
        else:
            raise Exception(f"Unexpected response: {result}")
    return {"enabled":tenant_enabled, "regional_url":found_url}
        

if __name__ == "__main__":
    #Example for a specific tenant, this can be a string or a list the default is all tenants in the config file. MAKE SURE THE NAME IS CORRECT(case sensitive) for specific tenants.
    #configs = get_target_tenant_configs(target_tenants="target-tenant-name")
    for tenant in tenants:
        print("-" * 15)
        result = check_for_tenant_in_all_regtions(tenant)
        if not result["enabled"]:
            #We can assume that the tenant is not enabled.
            print(f"{colors['RED']}This tenant is not enabled (Realm not available) for {tenant}{colors['RESET']}")
        #The tenant is enabled. Refresh token is inconsequential in this for testing if the tenant is active. 
        else:
            print(f"{colors['GREEN']}{tenant} is enabled, on regional url: {result['regional_url']}{colors['RESET']}")
        print("-" * 15)