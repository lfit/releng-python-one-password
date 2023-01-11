# python-one-password
Python code to extract useful information/data/reports from 1Password

Maintained by: Matthew Watkins <em>(Release Engineering)</em>


## Features

* Enumerates name and id values of vaults in your local 1Password database
* Excludes the default "Private" vault to prevent processing of personal data
* Has an configurable exclusion dictionary for removing further vaults from processing
* Allows for flexible specification of vaults (using either name or id value)
* Enumerates the appropriate vault items and adds metadata to an internal dictionary


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

	credential.py


## Usage

Simply call the script from the command line and it will output basic information about your vaults. If it is the first time you have run the script in a while, the main 1Password application may launch and prompt you to unlock your vault. You will be prompted for your passphrase or biometric data.

```
python-one-password (🌴 main) % ./credential.py --help
Usage: credential.py [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --debug  Debug/verbose output
  --help       Show this message and exit.

Commands:
  list   Lists the id/names of all vaults in the 1Password database
  stats  Gathers and reports on metadata from 1Password vaults
python-one-password (🌴 main) % ./credential.py list --help
### Processing 1Password Vaults ###

Usage: credential.py list [OPTIONS]

  Lists the id/names of all vaults in the 1Password database

Options:
  --help  Show this message and exit.
python-one-password (🌴 main) % ./credential.py list       
### Processing 1Password Vaults ###

ID                            NAME
nmyk5ccmeglgmu4l7vqgeuk3ua    Private
cqu623pi7vkfwuxtflhfpqjyby    Alljoyn Azure
aybebswcrbajtah3zeclnyw23q    Copied from IT Accounts
hp6scg3fdlyzqzqn7gqyx3pyqm    Copied from LF Internal Sites
qjeirfok77jutdtwhay4zu42qu    Domains & Registrars
647kt3iprbcgm6hykeve4gmmze    Hyperledger Infra
mv2wieanyalgisjhhwom4tflea    I.T.
6bar33zg5opi23vegebl2zn74e    Insights-IT
p6wtwojt5opgpankge4tk7rige    J Query Certificates
rfxhzmiiffvjwehntulmmidqhi    LF Corp Shared Vault
3bkq3c4sjkaha43fsbetzlfqey    LF HelloSign
vqyacgty4cku5sszf2vhcmqfuq    LF IT Finance Access
7v5msvbuz2i6g2tw5f3fjypj4i    LF Networking
72ycdwnelrihc3rdcy4uhaghfi    LF Virtual Trainers
tn4y2cveivccdpokn5zkzglmaq    My Linux Foundation
lkava6puzlvh5by5mo2ddhzfza    Product
ka7jamnsrvf52fyd4fwtq7p6tu    Release Engineering
5zk24mglr6o2ereikcrd67aasa    Shared Google Workspaces
pp6zwlxuihwoq4pd6lsadfcjqq    Shared Local Atlassian Logins

Number of vaults in database: 19
python-one-password (🌴 main) % ./credential.py -d stats -e "My Linux Foundation" -v "LF HelloSign"
Logging level set to debug/verbose
### Processing 1Password Vaults ###

Running command: op vault ls
ID                            NAME
nmyk5ccmeglgmu4l7vqgeuk3ua    Private
cqu623pi7vkfwuxtflhfpqjyby    Alljoyn Azure
aybebswcrbajtah3zeclnyw23q    Copied from IT Accounts
hp6scg3fdlyzqzqn7gqyx3pyqm    Copied from LF Internal Sites
qjeirfok77jutdtwhay4zu42qu    Domains & Registrars
647kt3iprbcgm6hykeve4gmmze    Hyperledger Infra
mv2wieanyalgisjhhwom4tflea    I.T.
6bar33zg5opi23vegebl2zn74e    Insights-IT
p6wtwojt5opgpankge4tk7rige    J Query Certificates
rfxhzmiiffvjwehntulmmidqhi    LF Corp Shared Vault
3bkq3c4sjkaha43fsbetzlfqey    LF HelloSign
vqyacgty4cku5sszf2vhcmqfuq    LF IT Finance Access
7v5msvbuz2i6g2tw5f3fjypj4i    LF Networking
72ycdwnelrihc3rdcy4uhaghfi    LF Virtual Trainers
tn4y2cveivccdpokn5zkzglmaq    My Linux Foundation
lkava6puzlvh5by5mo2ddhzfza    Product
ka7jamnsrvf52fyd4fwtq7p6tu    Release Engineering
5zk24mglr6o2ereikcrd67aasa    Shared Google Workspaces
pp6zwlxuihwoq4pd6lsadfcjqq    Shared Local Atlassian Logins

Key: nmyk5ccmeglgmu4l7vqgeuk3ua Value: Private
Key: cqu623pi7vkfwuxtflhfpqjyby Value: Alljoyn Azure
Key: aybebswcrbajtah3zeclnyw23q Value: Copied from IT Accounts
Key: hp6scg3fdlyzqzqn7gqyx3pyqm Value: Copied from LF Internal Sites
Key: qjeirfok77jutdtwhay4zu42qu Value: Domains & Registrars
Key: 647kt3iprbcgm6hykeve4gmmze Value: Hyperledger Infra
Key: mv2wieanyalgisjhhwom4tflea Value: I.T.
Key: 6bar33zg5opi23vegebl2zn74e Value: Insights-IT
Key: p6wtwojt5opgpankge4tk7rige Value: J Query Certificates
Key: rfxhzmiiffvjwehntulmmidqhi Value: LF Corp Shared Vault
Key: 3bkq3c4sjkaha43fsbetzlfqey Value: LF HelloSign
Key: vqyacgty4cku5sszf2vhcmqfuq Value: LF IT Finance Access
Key: 7v5msvbuz2i6g2tw5f3fjypj4i Value: LF Networking
Key: 72ycdwnelrihc3rdcy4uhaghfi Value: LF Virtual Trainers
Key: tn4y2cveivccdpokn5zkzglmaq Value: My Linux Foundation
Key: lkava6puzlvh5by5mo2ddhzfza Value: Product
Key: ka7jamnsrvf52fyd4fwtq7p6tu Value: Release Engineering
Key: 5zk24mglr6o2ereikcrd67aasa Value: Shared Google Workspaces
Key: pp6zwlxuihwoq4pd6lsadfcjqq Value: Shared Local Atlassian Logins
Python Dictionary created from 1Password Vault:
{'nmyk5ccmeglgmu4l7vqgeuk3ua': 'Private', 'cqu623pi7vkfwuxtflhfpqjyby': 'Alljoyn Azure', 'aybebswcrbajtah3zeclnyw23q': 'Copied from IT Accounts', 'hp6scg3fdlyzqzqn7gqyx3pyqm': 'Copied from LF Internal Sites', 'qjeirfok77jutdtwhay4zu42qu': 'Domains & Registrars', '647kt3iprbcgm6hykeve4gmmze': 'Hyperledger Infra', 'mv2wieanyalgisjhhwom4tflea': 'I.T.', '6bar33zg5opi23vegebl2zn74e': 'Insights-IT', 'p6wtwojt5opgpankge4tk7rige': 'J Query Certificates', 'rfxhzmiiffvjwehntulmmidqhi': 'LF Corp Shared Vault', '3bkq3c4sjkaha43fsbetzlfqey': 'LF HelloSign', 'vqyacgty4cku5sszf2vhcmqfuq': 'LF IT Finance Access', '7v5msvbuz2i6g2tw5f3fjypj4i': 'LF Networking', '72ycdwnelrihc3rdcy4uhaghfi': 'LF Virtual Trainers', 'tn4y2cveivccdpokn5zkzglmaq': 'My Linux Foundation', 'lkava6puzlvh5by5mo2ddhzfza': 'Product', 'ka7jamnsrvf52fyd4fwtq7p6tu': 'Release Engineering', '5zk24mglr6o2ereikcrd67aasa': 'Shared Google Workspaces', 'pp6zwlxuihwoq4pd6lsadfcjqq': 'Shared Local Atlassian Logins'}
Number of vaults in database: 19
Excluded vaults: 
    Private
    My Linux Foundation
Number of vaults excluded: 2
Number of vaults available: 17

Processing: 1 target vault(s)

Querying vault named: LF HelloSign
With id: 3bkq3c4sjkaha43fsbetzlfqey

Running command: op item list --format json --vault "LF HelloSign"
[
  {
    "id": "3nxq5ca2pnhv2txx3hmjmx6eku",
    "title": "HelloSign API",
    "tags": ["Shared-Shared-LF HelloSign API"],
    "version": 1,
    "vault": {
      "id": "3bkq3c4sjkaha43fsbetzlfqey",
      "name": "LF HelloSign"
    },
    "category": "SECURE_NOTE",
    "last_edited_by": "PBIB7FZ6BFARJHHHZZOOA4W3QI",
    "created_at": "2022-09-16T14:58:40Z",
    "updated_at": "2022-09-16T14:58:40Z",
    "additional_information": "API keys"
  },
  {
    "id": "nke3pkxcpjit7dv7iuoh6tvzr4",
    "title": "e-signing HelloSign LF CLA",
    "tags": ["Shared-Johnson \u0026 Heather"],
    "version": 1,
    "vault": {
      "id": "3bkq3c4sjkaha43fsbetzlfqey",
      "name": "LF HelloSign"
    },
    "category": "LOGIN",
    "last_edited_by": "PBIB7FZ6BFARJHHHZZOOA4W3QI",
    "created_at": "2022-08-30T18:06:41Z",
    "updated_at": "2022-08-30T18:06:41Z",
    "additional_information": "e-signing@linuxfoundation.org",
    "urls": [
      {
        "primary": true,
        "href": "https://hellosign.com"
      }
    ]
  },
  {
    "id": "m2b5o6jsqys54j67a6fvdju7pa",
    "title": "HelloSign Dev",
    "tags": ["Shared-Shared-LF HelloSign API"],
    "version": 1,
    "vault": {
      "id": "3bkq3c4sjkaha43fsbetzlfqey",
      "name": "LF HelloSign"
    },
    "category": "LOGIN",
    "last_edited_by": "PBIB7FZ6BFARJHHHZZOOA4W3QI",
    "created_at": "2022-09-16T14:58:40Z",
    "updated_at": "2022-09-16T14:58:40Z",
    "additional_information": "e-signing-dev@linuxfoundation.org",
    "urls": [
      {
        "primary": true,
        "href": "https://www.hellosign.com/"
      }
    ]
  }
]

### VAULT JSON DATA ###
[{'id': '3nxq5ca2pnhv2txx3hmjmx6eku', 'title': 'HelloSign API', 'tags': ['Shared-Shared-LF HelloSign API'], 'version': 1, 'vault': {'id': '3bkq3c4sjkaha43fsbetzlfqey', 'name': 'LF HelloSign'}, 'category': 'SECURE_NOTE', 'last_edited_by': 'PBIB7FZ6BFARJHHHZZOOA4W3QI', 'created_at': '2022-09-16T14:58:40Z', 'updated_at': '2022-09-16T14:58:40Z', 'additional_information': 'API keys'}, {'id': 'nke3pkxcpjit7dv7iuoh6tvzr4', 'title': 'e-signing HelloSign LF CLA', 'tags': ['Shared-Johnson & Heather'], 'version': 1, 'vault': {'id': '3bkq3c4sjkaha43fsbetzlfqey', 'name': 'LF HelloSign'}, 'category': 'LOGIN', 'last_edited_by': 'PBIB7FZ6BFARJHHHZZOOA4W3QI', 'created_at': '2022-08-30T18:06:41Z', 'updated_at': '2022-08-30T18:06:41Z', 'additional_information': 'e-signing@linuxfoundation.org', 'urls': [{'primary': True, 'href': 'https://hellosign.com'}]}, {'id': 'm2b5o6jsqys54j67a6fvdju7pa', 'title': 'HelloSign Dev', 'tags': ['Shared-Shared-LF HelloSign API'], 'version': 1, 'vault': {'id': '3bkq3c4sjkaha43fsbetzlfqey', 'name': 'LF HelloSign'}, 'category': 'LOGIN', 'last_edited_by': 'PBIB7FZ6BFARJHHHZZOOA4W3QI', 'created_at': '2022-09-16T14:58:40Z', 'updated_at': '2022-09-16T14:58:40Z', 'additional_information': 'e-signing-dev@linuxfoundation.org', 'urls': [{'primary': True, 'href': 'https://www.hellosign.com/'}]}]
### /VAULT JSON DATA ###
### Script Completed ###
```
