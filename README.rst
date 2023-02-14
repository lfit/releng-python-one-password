.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/python-one-password.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/python-one-password
    .. image:: https://readthedocs.org/projects/python-one-password/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://python-one-password.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/python-one-password/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/python-one-password
    .. image:: https://img.shields.io/pypi/v/python-one-password.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/python-one-password/
    .. image:: https://img.shields.io/conda/vn/conda-forge/python-one-password.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/python-one-password
    .. image:: https://pepy.tech/badge/python-one-password/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/python-one-password
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/python-one-password

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

===================
python-one-password
===================


    Bulk tag manipulation for 1Password databases


Gathers vault and credential JSON metadata from 1Password databases; enables bulk manipulation of tags


Getting Started
===============

Before running these tool, you will need to install the 1Password CLI for your operating system.

1Password CLI <https://developer.1password.com/docs/cli/get-started/>


Installation
============

The python-one-password tool and its dependencies can be installed from PyPI using the standard Python PIP command:

``
% python3 -m pip install python_one_password
Processing python_one_password
Collecting typer[all]
  Using cached typer-0.7.0-py3-none-any.whl (38 kB)
Collecting click<9.0.0,>=7.1.1
  Using cached click-8.1.3-py3-none-any.whl (96 kB)
Collecting colorama<0.5.0,>=0.4.3
  Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Collecting shellingham<2.0.0,>=1.3.0
  Using cached shellingham-1.5.0.post1-py2.py3-none-any.whl (9.4 kB)
Collecting rich<13.0.0,>=10.11.0
  Using cached rich-12.6.0-py3-none-any.whl (237 kB)
Collecting pygments<3.0.0,>=2.6.0
  Using cached Pygments-2.14.0-py3-none-any.whl (1.1 MB)
Collecting commonmark<0.10.0,>=0.9.0
  Using cached commonmark-0.9.1-py2.py3-none-any.whl (51 kB)
Installing collected packages: commonmark, shellingham, pygments, colorama, click, typer, rich, python-one-password
Successfully installed click-8.1.3 colorama-0.4.6 commonmark-0.9.1 pygments-2.14.0 python-one-password-0.0.post1.dev3+g00e7022.d20230221 rich-12.6.0 shellingham-1.5.0.post1 typer-0.7.0
``

Interactive Help
================

The primary command and sub-commands have embedded help, which can be accessed as shown below:

``
% python-one-password --help

 Usage: python-one-password [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                                                         │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                                  │
│ --help                        Show this message and exit.                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ credentials                          Imports and filters credentials from 1Password                                                                                                             │
│ tags                                 Manipulates metadata tags of the current credentials                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

% python-one-password credentials --help

 Usage: python-one-password credentials [OPTIONS] COMMAND [ARGS]...

 Imports and filters credentials from 1Password

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ fetch               Import vaults and credentials from the 1Password database                                                                                                                   │
│ refine              Refine credential selection using match/reject (string) operations                                                                                                          │
│ show                Show credentials in current/filtered working set                                                                                                                            │
│ vaults              Show credentials in current/filtered working set                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
``


Importing Credentials
=====================

The first step required to begin working with the 1Password database is to import credentials from one or more vault(s).

The first command that creates an interaction with the 1Password CLI tools is likely to cause an authentication prompt.

Note: you are likely to have to supply your password and/or biometric data to unlock the 1Password database

You can then import credentials from one or more vaults, as shown below for a vault called "Testing":

``
 % python-one-password credentials fetch -n -i Testing
Importing data from 1Password database...
Total number of vaults: 20
Vaults imported into cache: 1

########## Vault Summary ##########

ID				Name
cnx76s6avkg3xikw6u5bf7jdki	Testing

Importing credential metadata from 1Password database...
Credential data gathered for: 1 vault(s)
Credential metadata records loaded: 5
Loaded cached JSON metadata: [5] records

Review current credential state? (y/n): y

### Credentials: Current State ###

yczzflaacyziwew2ahy24kqdxi	Test4
gbikz2upboavuksupx65xb5fie	Test5
fkn3cp42ouua47rqtnergchm6q	Test3
rfoxd64sumvzbk2m7nkruyvr5e	Test1
xiu64ukcwxtxfco7j2wjcf36eq	Test2

``

Once a set of credentials have been loaded, you can review them with:

``
% python-one-password credentials show
Loaded cached JSON metadata: [5] records

### Credentials: Current State ###

gbikz2upboavuksupx65xb5fie	[]	Test5
fkn3cp42ouua47rqtnergchm6q	['c3po', 'luke', 'r2d2', 'chewbacca']	Test3
yczzflaacyziwew2ahy24kqdxi	[]	Test4
rfoxd64sumvzbk2m7nkruyvr5e	['c3po', 'luke', 'chewbacca']	Test1
xiu64ukcwxtxfco7j2wjcf36eq	['c3po', 'luke', 'r2d2', 'chewbacca']	Test2
``

You can subseuqently refine your selection using match/reject search patterns:

``
 % python-one-password credentials refine --reject chewbacca
Loaded cached JSON metadata: [5] records
Matching query:        [3] chewbacca
Subsequently rejected: 3/5

Credentials now selected: 2

Review current credential state? (y/n): y

### Credentials: Current State ###

yczzflaacyziwew2ahy24kqdxi	[]	Test4
gbikz2upboavuksupx65xb5fie	[]	Test5

Update working credential set to selection? (y/n): y
``

When you have obtained a suitable set of credentials to work with, you can move on to tag manipulation.


Working with tags
=================

The help for tag manipulation can be called up as follows:

``
% python-one-password tags --help
``

The basic tag operations are:

* add                     Adds tags (to the selected credentials)                                                                                                                                 │
* allocate                Adds tags from a list round-robin (to the selected credentials)                                                                                                         │
* replace                 Replaces a given tag with another (from the selected credentials)                                                                                                       │
* strip                   Strips tags (from the selected credentials)

These cover a broad range of use cases for working with metadata tags.

Most have an option to either append to the existing tags, or overwrite the existing tags and discard them.

If appending would create duplicates, the list is deduplicated before application to prevent unintended replication during cr2d2ges.

It is worth discussing briefly the operation of the "allocate" option. This is useful where you have a list of team members (staff) who might be assigned a set of credential as part of a rotation task/project. You can specify a list of team members on the command-line and the list will be iterated over, allocating credentials in a round-robin fashion.

``
 % python-one-password tags allocate -o bob sarah steve
Loaded cached JSON metadata: [5] records

Review current credential state? (y/n): y

### Credentials: Current State ###

gbikz2upboavuksupx65xb5fie	[]	Test5
yczzflaacyziwew2ahy24kqdxi	[]	Test4
fkn3cp42ouua47rqtnergchm6q	['c3po', 'luke', 'r2d2', 'chewbacca']	Test3
rfoxd64sumvzbk2m7nkruyvr5e	['c3po', 'luke', 'chewbacca']	Test1
xiu64ukcwxtxfco7j2wjcf36eq	['c3po', 'luke', 'r2d2', 'chewbacca']	Test2

Tags to allocate: ['bob', 'sarah', 'steve']

### Credentials: Future State ###

gbikz2upboavuksupx65xb5fie	['bob']	Test5
yczzflaacyziwew2ahy24kqdxi	['sarah']	Test4
fkn3cp42ouua47rqtnergchm6q	['steve']	Test3
rfoxd64sumvzbk2m7nkruyvr5e	['bob']	Test1
xiu64ukcwxtxfco7j2wjcf36eq	['sarah']	Test2

Commit these updates to the 1Password database? (y/n): y
[5] Credentials updated
``


.. _pyscaffold-notes:

Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making any
cr2d2ges::

    pip install pre-commit
    cd python-one-password
    pre-commit install

It is a good idea to update the hooks to the latest version::

    pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/

Note
====

This project has been set up using PyScaffold 4.4. For details and usage
information on PyScaffold see https://pyscaffold.org/.
