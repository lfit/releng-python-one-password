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

"""Functions to load/save cached JSON metadata"""

__author__ = "Matthew Watkins"

# Standard imports, alphabetical order ###
import json
import logging
import os
import os.path
import sys
import time
from typing import Any, List

# Setup logging
log = logging.getLogger(__name__)


# Define the filesystem names of various JSON metadata cache files
datastores = {
    "vault_summary": "vault.summary.metadata.json",
    "vaults_detail": "vault.detailed.metadata.json",
    "vault_credentials": "vault.credentials.metadata.json",
    "credentials": "credentials.metadata.json",
}


# File/caching operations


def load_json_file(filename: str) -> str:
    """Returns JSON data object from a given file"""
    try:
        with open(filename, encoding="utf-8") as open_file:
            data = json.loads(open_file.read())
            log.debug("JSON read from file: %s", filename)
    except IOError as error:
        log.error("Error reading JSON from file: %s", filename)
        log.error(error)
        sys.exit(1)
    return data


def save_json_file(json_data: List[str], filename: str):
    """Saves a JSON data object to disk"""
    try:
        with open(filename, "w", encoding="utf-8") as write_file:
            json.dump(json_data, write_file)
            log.debug("JSON written to file: %s", filename)
    except IOError as error:
        log.error("Error writing JSON to file: %s", filename)
        log.error(error)
        sys.exit(1)


def validate_cache(filename: str):
    """Checks local metadata for freshness"""
    if not check_cache_age(filename, 3600):
        refresh_cache()


def get_file_age(filepath: str) -> float:
    """Returns the age of a file on disk in seconds"""
    return time.time() - os.path.getmtime(filepath)


def load_cache(data_store: str):
    """Loads data from the filesystem and returns the JSON"""
    log.debug("Request to load records from cache: %s", data_store)
    if filename := datastores.get(data_store, None):
        # Check cache validity
        validate_cache(filename)
        data = load_json_file(filename)
        log.info("Loaded cached JSON metadata: [%s] records", len(data))
        log.debug("\n%s", data)
        return data
    log.error("The requested cache does not exist: %s", data_store)
    sys.exit(1)


def save_cache(json_data: Any, data_store: str):
    """Saves JSON data to the filesystem"""
    log.debug("Saving [%s] records to cache: %s", len(json_data), data_store)
    if filename := datastores.get(data_store, None):
        save_json_file(json_data, filename)
        return
    log.error("The requested cache does not exist: %s", data_store)
    sys.exit(1)


def check_cache_age(filename: str, max_age: int) -> bool:
    """Returns cache validity when given a maximum age (in seconds)"""
    log.debug("Cache lifetime/expiry set to: %s seconds", max_age)
    if os.path.isfile(filename):
        age = get_file_age(filename)
        if age < max_age:
            return True
        return False
    log.error("The requested file could not be opened: %s", filename)
    sys.exit(1)


# TODO: check metadata modification times and version numbers; selectively reload data
def refresh_cache():
    """Currently throws an error; could eventually invoke cache validation"""
    log.error("The local cache file(s) are invalid or have expired")
    log.error("Please reload credentials from the required vault(s)")
    sys.exit(1)
