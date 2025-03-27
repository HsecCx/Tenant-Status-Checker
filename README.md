# Project Title: Tenant IAM Region Checker

A concurrent Python script that verifies whether specific Checkmarx tenants are enabled in different IAM regional endpoints. Useful for automation, diagnostics, or validation across cloud regions.

---

# 🚀 Features

- Checks if a tenant is enabled across multiple IAM regions
- Multi-threaded for fast performance
- Automatically writes results to a CSV file
- Supports filtering by tenant and region
- Highlights results in the console with color-coded output

---

# 🛠️ Installation

Make sure you have Python 3.8+ installed and install the required dependencies (if any).

```
# Clone the repository
git clone https://github.com/your-username/tenant-iam-checker.git
cd tenant-iam-checker

# Install dependencies
pip install -r requirements.txt
```

---

# 💡 Usage

```
# Check tenants across all regions (default)
python script.py --tenants acme checkmate testco

# Check tenants only in US and EU regions
python script.py --tenants acme checkmate --regions US EU

# Limit the number of threads
python script.py --tenants acme --max_threads 4
```

If no `--tenants` argument is passed, the script will read from a `tenants.txt` file in the same directory.

The output will be saved to `tenant_status.csv`.

---

# 📁 Project Structure

```
tenant-iam-checker/
├── script.py           # Main script
├── tenants.txt         # Optional file listing tenants to check
├── tenant_status.csv   # Output CSV with status results
├── README.md           # Project overview and usage guide
```

---

# 📄 License

This project is licensed under the MIT License.

