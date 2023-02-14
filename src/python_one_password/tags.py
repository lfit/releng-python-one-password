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

"""Provides a library of functions for manipulating tag metadata"""

__author__ = "Matthew Watkins"

# Standard imports, alphabetical order
import logging
import logging.handlers
import sys
from typing import List

# External modules
import typer

# Bundled modules
import python_one_password.caching as caching
import python_one_password.functions as f

# Setup logging
log = logging.getLogger(__name__)


# Define command structure with typer module
app = typer.Typer()


# Tag operations


@app.command()
def add(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        show_default=False,
        help="Overwrite any pre-existing tags (they are otherwise preserved)",
    ),
    tags: List[str] = typer.Argument(
        None,
        show_default=False,
        help="Add tag(s) to the currently selected credentials",
    ),
):
    """Adds tags (to the selected credentials)"""
    f.startup_tasks(debug)
    if len(tags) == 0:
        log.error("To update credentials you must specify at least one tag")
        sys.exit(1)
    # Check for duplicate tags
    if f.contains_duplicates(tags):
        log.error("You cannot specify duplicate tags!")
        sys.exit(1)
    credential_data = caching.load_cache("credentials")
    f.credential_summary(credential_data, False, True)
    if overwrite:
        log.warning("\nWarning: addition operation will overwrite existing tags")
    log.info("\nTag(s) to apply: %s", tags)
    f.tags_update(credential_data, tags, overwrite, False)


@app.command()
def allocate(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        show_default=False,
        help="Overwrite any pre-existing tags (they are otherwise preserved)",
    ),
    tags: List[str] = typer.Argument(
        None,
        show_default=False,
        help="Allocate tag(s) to the currently selected credentials",
    ),
):
    """Adds tags from a list round-robin (to the selected credentials)"""
    # Useful for allocating credentials to users in a team, etc
    f.startup_tasks(debug)
    # Check for duplicate tags
    if len(tags) < 2:
        log.error("Round-robin allocation requires at least two tags!")
        sys.exit(1)
    # Check for duplicate tags; preserving order
    if f.contains_duplicates(tags):
        log.error("You cannot specify duplicate tags!")
        sys.exit(1)
    credential_data = caching.load_cache("credentials")
    f.credential_summary(credential_data, False, True)
    log.info("\nTags to allocate: %s", tags)
    f.tags_update(credential_data, tags, overwrite, True)


@app.command()
def strip(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    )
):
    """Strips tags (from the selected credentials)"""
    f.startup_tasks(debug)
    credential_data = caching.load_cache("credentials")
    f.credential_summary(credential_data, False, True)
    log.warning("Stripping all tags from credentials")
    f.tags_update(credential_data, [], True, False)


@app.command()
def replace(
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        show_default=False,
        help="Enable verbose debug output/logging",
    ),
    search: str = typer.Argument(
        None, show_default=False, help="Tag to match and substitute"
    ),
    # pylint: disable-next=W0621
    replace: str = typer.Argument(
        None, show_default=False, help="Replacement for existing tag"
    ),
):
    """Replaces a given tag with another (from the selected credentials)"""
    f.startup_tasks(debug)
    if not search or not replace:
        log.error("You must specify both a search and a replace string!")
        sys.exit(1)
    credential_data = caching.load_cache("credentials")
    # credential_summary(credentials, False)
    f.tag_search_replace(credential_data, search, replace)
