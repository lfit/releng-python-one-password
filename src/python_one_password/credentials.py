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

# Standard imports, alphabetical order
import logging
import logging.handlers
from typing import List, Optional

# External modules
import typer

# Bundled modules
import python_one_password.caching as caching
import python_one_password.functions as f

# Setup logging
log = logging.getLogger(__name__)


# Define command structure with typer module
app = typer.Typer()


# Credential operations


@app.command()
def fetch(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    ),
    include: Optional[List[str]] = typer.Option(
        ["All"],
        "--include",
        "-i",
        envvar="OP_VAULT_INC",
        help="Includes the specified vault(s) from processing",
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        envvar="OP_VAULT_EXC",
        help="Excludes the specified vault(s) from processing",
    ),
    no_tags: bool = typer.Option(
        False, "--no-tags", "-n", help="Hide metadata tags in credential summary/output"
    ),
):
    """Import vaults and credentials from the 1Password database"""
    f.startup_tasks(debug)
    f.validate_import_data_opts(include, exclude)
    vaults_dictionary = f.populate_vault_json(include, exclude)
    f.show_vault_summary(vaults_dictionary)
    f.import_credentials(vaults_dictionary)
    credential_data = f.caching.load_cache("credentials")
    f.credential_summary(credential_data, no_tags, True)


@app.command()
def vaults(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    )
):
    """Show credentials in current/filtered working set"""
    f.startup_tasks(debug)
    vault_summ_cmd = "op vaults list"
    raw_data = f.run_cmd_mp(vault_summ_cmd)
    log.info(raw_data)


@app.command()
def show(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    ),
    no_tags: bool = typer.Option(
        False, "--no-tags", "-n", help="Hide metadata tags in credential summary/output"
    ),
):
    """Show credentials in current/filtered working set"""
    f.startup_tasks(debug)
    credential_data = caching.load_cache("credentials")
    f.credential_summary(credential_data, no_tags, False)


@app.command()
def refine(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    ),
    no_tags: bool = typer.Option(
        False, "--no-tags", "-n", help="Hide metadata tags in credential summary/output"
    ),
    match: Optional[List[str]] = typer.Option(
        None,
        "--match",
        "-m",
        help="Match/select credentials containing the specified text",
    ),
    reject: Optional[List[str]] = typer.Option(
        None,
        "--reject",
        "-r",
        help="Reject/exclude credentials containing the specified text",
    ),
    ignore_case: bool = typer.Option(
        False,
        "--ignore-case",
        "-i",
        show_default=True,
        help="Ignore case when matching strings in credentials",
    ),
):
    """Refine credential selection using match/reject (string) operations"""
    f.startup_tasks(debug)
    f.validate_filter_items_opts(match, reject)
    credential_data = f.filter_credentials(match, reject, ignore_case)
    f.credential_summary(credential_data, no_tags, True)
    if f.prompt("Update working credential set to selection?"):
        caching.save_cache(credential_data, "credentials")
    else:
        log.info("Select/reject did not modify credential database")
