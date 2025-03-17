## Tenant OAuth Token Generator 
- This script is used to generate OAuth tokens for multiple Checkmarx AST tenants by reading configurations from a config file. It supports retrieving tokens for all tenants or specific ones, with color-coded console output for better visibility. 

## Features 
- Retrieve OAuth tokens for all tenants or specific ones. - Color-coded output: Green (token successfully generated), Yellow (invalid refresh token), Red (tenant not enabled). - Reads tenant configurations from ALL_CONFIGS. - Supports single and multiple tenant filtering.

## Usage 

1) Install Dependencies: 
pip install requests 

2) !!Update or create tenants.txt to have all your tenants you want to check for!!. Seperate each tenant by a line break

3) Running the Script: To test generating tokens for all tenants (default): python script.py. 

4) Expected Output for the different statuses: 

---------------- \<Tenant> is enabled, on regional url: \<regional_url> --------------- (This will be green)

---------------- This tenant is not enabled (Realm not available) for \<tenant> ---------------- (This will be red)

## Code Overview 
``` 
def check_for_tenant_in_all_regtions(tenant: str) -> dict:
```
Checks if the tenants in the tenant.txt file exist on any regional url

- Color Legend: GREEN (\033[32m) → Tenant is enabled (refresh token is inconsequential for checking if the tenant is enabled) 
- RED (\033[31m) → Tenant not enabled, RESET (\033[0m) → Resets color. ## Credits - Developed by [Your Name].
