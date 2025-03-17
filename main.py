from utils.test_tenant_enabled import generate_oauth_token_test,load_config

ALL_CONFIGS = load_config()
colors = {
    "GREEN":"\033[32m",
    "YELLOW":"\033[33m",
    "RED":"\033[31m",
    "RESET":"\033[0m"
    }

def get_target_tenant_configs(target_tenants: str | list = "all"):
    relevant_configs = []
    for config in ALL_CONFIGS.get("tenants", []):
        if target_tenants == "all" or (isinstance(target_tenants, list) and config["tenant_name"] in target_tenants) or config["tenant_name"] == target_tenants:
            relevant_configs.append(config)
    return relevant_configs

if __name__ == "__main__":
    #Example for a specific tenant, this can be a string or a list the default is all tenants in the config file. MAKE SURE THE NAME IS CORRECT(case sensitive) for specific tenants.
    #configs = get_target_tenant_configs(target_tenants="target-tenant-name")
    configs = get_target_tenant_configs()
    for config in configs:
        print("-" * 15)
        oauth_token = generate_oauth_token_test(config)
        if "realm not enabled" in oauth_token.lower():
            #We can assume that the tenant is not enabled.
            print(f"{colors['RED']}This tenant is not enabled (Realm not available) for {config['tenant_name']}{colors['RESET']}")
        #The tenant is enabled. Refresh token is inconsequential in this for testing if the tenant is active. 
        elif "invalid refresh token" in oauth_token.lower():
            print(f"{colors['GREEN']}{config['tenant_name']} is enabled{colors['RESET']}")
        else:
            print(oauth_token)
        print("-" * 15)