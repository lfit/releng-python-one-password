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
from python_one_password.credentials import app as credentials
from python_one_password.tags import app as tags

# Define command structure with typer module
app = typer.Typer()


# Additional sub-commands


app.add_typer(
    credentials,
    name="credentials",
    help="Imports and filters credentials from 1Password",
)

app.add_typer(
    tags,
    name="tags",
    help="Manipulates metadata tags of the current credentials",
)


def run():
    app()
