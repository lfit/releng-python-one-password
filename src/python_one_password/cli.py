#!/usr/bin/env python3

# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2023 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials are made
# available under the terms of the Apache-2.0 license which accompanies this
# distribution, and is available at
# https://opensource.org/licenses/Apache-2.0
##############################################################################

"""Python wrapper for manipulating 1Password credential metadata/tags"""

__author__ = "Matthew Watkins"

# External modules
import typer

# Bundled modules
import python_one_password.credentials as credentials
import python_one_password.tags as tags

# Define command structure with typer module

python_one_password = typer.Typer()
python_one_password.add_typer(
    credentials.python_one_password,
    name="credentials",
    help="Imports and filters credentials from 1Password",
)
python_one_password.add_typer(
    tags.python_one_password,
    name="tags",
    help="Manipulates metadata tags of the current credentials",
)


def run():
    python_one_password()
