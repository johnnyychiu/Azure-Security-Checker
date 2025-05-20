# Azure-Security-Checker
An automated tool to assess Azure cloud security settings for security engineers and pentesters.

## Overview

Azure Security Checker is a lightweight CLI tool that helps security engineers and pentesters quickly identify common security issues in Microsoft Azure subscriptions.  
It checks public resources, common misconfigurations, and provides an easy-to-read Markdown report.

---

## Features

- ✅ List all public storage accounts and VMs
- ✅ Identify resources with open public access
- ✅ Check for weak security configurations (e.g. default passwords, no HTTPS)
- ✅ Export findings to a Markdown report
- ✅ Simple CLI usage

---

## Requirements

- Python 3.8+
- `azure-identity`, `azure-mgmt-resource`, `azure-mgmt-storage`, `azure-mgmt-compute`
- Azure account credentials (via CLI login or environment variables)
- OS: Windows / macOS / Linux

---

## Installation

```bash
git clone https://github.com/[your-username]/azure-security-checker.git
cd azure-security-checker
pip install -r requirements.txt
```
---

## Usage

Basic usage:
```
python3 azure_security_checker.py --subscription [AZURE_SUBSCRIPTION_ID]
```

Example:
```
python3 azure_security_checker.py --subscription 12345678-aaaa-bbbb-cccc-123456789abc --output result.md
```

Options:
```
--subscription : Azure subscription ID (required)
--output : (Optional) Output report file name (default: result.md)
```

---

## Quick Start

1. Clone this repo and install dependencies

2. Login to Azure CLI:
```
az login
```

3. Run the tool with your Azure subscription ID

4. Check the generated report in the current folder
