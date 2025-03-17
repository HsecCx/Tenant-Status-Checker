## Tenant OAuth Token Generator 
- This script is used to generate OAuth tokens for multiple Checkmarx AST tenants by reading configurations from a config file. It supports retrieving tokens for all tenants or specific ones, with color-coded console output for better visibility. 

## Features 
- Retrieve OAuth tokens for all tenants or specific ones. - Color-coded output: Green (token successfully generated), Yellow (invalid refresh token), Red (tenant not enabled). - Reads tenant configurations from ALL_CONFIGS. - Supports single and multiple tenant filtering. +

## Usage 

1) Install Dependencies: 
pip install requests 

2) Update Configuration: Make sure your tenant configurations are correctly defined in your config file. 

3) Running the Script: To generate tokens for all tenants (default): python script.py. 

    - To generate a token for a specific tenant: configs = get_target_tenant_configs(target_tenants="target-tenant-name"). 

    - To generate tokens for multiple tenants: configs = get_target_tenant_configs(target_tenants=["tenant1","tenant2"]). 

4) Expected Output for the different statuses: 

---------------- Successfully generated token for tenant1. This tenant is enabled --------------- 

---------------- This tenant is not enabled (Realm not available) for tenant2 ----------------

--------------- tenant3 is enabled but the refresh token is invalid --------------- 

## Configuration Structure Your tenant configuration should be structured as follows: 

```
{"tenants":
    [
    {"api_url":"https://<subdomain>.ast.checkmarx.net/api",
    "iam_url":"https://<subdomain>.iam.checkmarx.net/auth/realms/",
    "api_key":"<apikey>",
    "tenant_name":"<tenant_name>"}
    ]
    
}
```


## Code Overview 
``` 
get_target_tenant_configs(target_tenants: str | list = "all"):
```
Filters tenants based on the provided target_tenants (single string or list). Returns all tenants if "all" is provided. - generate_oauth_token(config): Generates the OAuth token for a given tenant using the provided configuration. 

- Color Legend: GREEN (\033[32m) → Token generated successfully, 
- YELLOW (\033[33m) → Invalid refresh token, 
- RED (\033[31m) → Tenant not enabled, RESET (\033[0m) → Resets color. ## Credits - Developed by [Your Name]. Uses 