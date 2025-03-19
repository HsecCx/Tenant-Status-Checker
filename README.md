## Tenant OAuth Token Generator 
- This script is used to test tenants to see if they are still live. It outputs a CSV letting you know if the tenant is enabled or not.

## Features 
- Retrieve OAuth tokens for all tenants or specific ones. 
- Color-coded output: Green (tenant enabled),Red (tenant not enabled). 
- Reads tenant configurations from tenants.txt or can take them as cli arguments. - Supports single and multiple tenant filtering.

## Usage 

1) Install Dependencies: 
pip install requests 

2) **Either pass the tenants as CLI args or update or create tenants.txt to have all your tenants you want to check for** 
    - Seperate each tenant by a line break in the tenants file or as a space when passing as the argument --tenants

3) Running the Script: To test generating tokens for all tenants (default):
  ```
  python main.py
```
```
python.py main.py --tenants <tenant1> <tenant2>
```

5) Expected Output:
- A csv with Tenant Name, Status, Regional URL(s)
- If passed by cli, there will also be ouput in the console
