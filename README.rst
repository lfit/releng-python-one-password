

.. image:: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
    :alt: Project generated in Python
    :target: https://www.python.org/

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

===================
python-one-password
===================


    Tag editor for 1Password


Gathers vault and credential JSON metadata from 1Password databases; enables bulk manipulation of tags


Getting Started
===============

Before running these tools, you will need to install the 1Password CLI for your operating system.

1Password CLI <https://developer.1password.com/docs/cli/get-started/>


Installation
============

The python-one-password tool and its dependencies can be installed from PyPI
using the standard Python PIP command:

``% python3 -m pip install python_one_password``

Interactive Help
================

The primary command and sub-commands have embedded help, which can be accessed
as shown below::

    % python-one-password --help
    % python-one-password credentials --help
    % python-one-password tags --help


Importing Credentials
=====================

The first step required to begin working with the 1Password database is to
import credentials from one or more vault(s).

The first command that creates an interaction with the 1Password CLI tools is
likely to generate an authentication prompt.

Note: supply your password and/or biometric data to unlock the 1Password database if/when prompted

You can then import credentials from one or more vaults, as shown below for a vault called "Testing"::

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

Once a set of credentials have been loaded, you can review them with::

    % python-one-password credentials show
    Loaded cached JSON metadata: [5] records

    ### Credentials: Current State ###

    gbikz2upboavuksupx65xb5fie	[]	Test5
    fkn3cp42ouua47rqtnergchm6q	['c3po', 'luke', 'r2d2', 'chewbacca']	Test3
    yczzflaacyziwew2ahy24kqdxi	[]	Test4
    rfoxd64sumvzbk2m7nkruyvr5e	['c3po', 'luke', 'chewbacca']	Test1
    xiu64ukcwxtxfco7j2wjcf36eq	['c3po', 'luke', 'r2d2', 'chewbacca']	Test2

You can subsequently refine your selection using match/reject search patterns::

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

When you have obtained a suitable set of credentials to work with, you can move
on to tag manipulation.


Working with Tags
=================

The help for tag manipulation can be called up as follows:

``% python-one-password tags --help``

The basic tag operations are:

* add         Adds tags (to the selected credentials)                                                                                                                                 │
* allocate    Adds tags from a list round-robin (to the selected credentials)                                                                                                         │
* replace     Replaces a given tag with another (from the selected credentials)                                                                                                       │
* strip       Strips tags (from the selected credentials)

These cover a broad range of use cases for working with metadata tags.

Most have an option to either append to the existing tags, or overwrite the
existing tags and discard them.

If appending would create duplicates, the list is deduplicated before
application to prevent unintended replication during changes.

It is worth discussing briefly the operation of the "allocate" option. This is
useful where you have a list of team members (staff) who might be assigned a
set of credential as part of a rotation task/project. You can specify a list of
team members on the command-line and the list will be iterated over, allocating
credentials in a round-robin fashion.::

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


Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making
any changes::

    % pip install pre-commit
    % cd python-one-password
    % pre-commit install

It is a good idea to update the hooks to the latest version::

``% pre-commit autoupdate``

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/
