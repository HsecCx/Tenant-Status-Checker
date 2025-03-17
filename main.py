from utils.generate_oauth_token import generate_oauth_token,load_config

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
    configs = get_target_tenant_configs()
    for config in configs:
        print("-" * 15)
        oauth_token = generate_oauth_token(config)
        if "Error" not in oauth_token:
            print(f"{colors['GREEN']}Successfully generated token for {config['tenant_name']}. This tenant is enabled{colors['RESET']}")
        else:
            if "realm not enabled" in oauth_token.lower():
                print(f"{colors['RED']}This tenant is not enabled (Realm not available) for {config['tenant_name']}{colors['RESET']}")
            elif "invalid refresh token" in oauth_token.lower():
                print(f"{colors['YELLOW']}{config['tenant_name']} is enabled but the refresh token is invalid{colors['RESET']}")
            else:
                print(oauth_token)
        print("-" * 15)