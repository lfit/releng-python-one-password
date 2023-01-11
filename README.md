# python-one-password
Python code to extract useful information/data/reports from 1Password

Maintained by: Matthew Watkins <em>(Release Engineering)</em>


## Features

* Enumerates name and id values of vaults in your local 1Password database
* Has an editable exclusion dictionary for removing vaults from scanning
* Enurates the items in each vault and adds them to a dictionary
* Creates a global dictionary containing all items from all vaults


### Pre-requisites

You will need to make sure you have installed the latest 1Password CLI tools:

A guide, including download locations for different platforms, can be found here:

https://developer.1password.com/docs/cli/get-started/

Make sure the one password tool is available in your PATH after installation.

You can test this as shown below:

```
mwatkins % op --version
2.6.0
```

You will also need to ensure you have Python3 installed and available from your shell.

If you Python3 interpreter is somewhere other than:

	/usr/bin/python3
	
You will need to edit the first line of the script to match your installation location:

	python-op.py


## Usage

Simply call the script from the command line and it will output basic information about your vaults. If it is the first time you have run the script in a while, the main 1Password application may launch and prompt you to unlock your vault. You will be prompted for your passphrase or biometric data.

```
python-one-password (🌴 main) % ./python-op.py 

### Processing 1Password Vaults ###

Number of vaults in database:  19
Number of vaults excluded:  2
Number of vaults to process:  17 

Processing Vault: "J Query Certificates"
Processing Vault: "LF Networking"
Processing Vault: "I.T."
Processing Vault: "Hyperledger Infra"
Processing Vault: "LF HelloSign"
Processing Vault: "LF IT Finance Access"
Processing Vault: "Copied from LF Internal Sites"
Processing Vault: "Insights-IT"
Processing Vault: "Product"
Processing Vault: "Shared Google Workspaces"
Processing Vault: "Copied from IT Accounts"
Processing Vault: "Release Engineering"
Processing Vault: "LF Virtual Trainers"
Processing Vault: "LF Corp Shared Vault"
Processing Vault: "Shared Local Atlassian Logins"
Processing Vault: "Alljoyn Azure"
Processing Vault: "Domains & Registrars"

### Script Completed ###
```

For much more details output, simply edit the script and enable the debugging flag, then run again.

```
# Set to enable verbose output
debug = True
```