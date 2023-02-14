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

"""Shared functions for use when interacting with 1Password"""

__author__ = "Matthew Watkins"

import json
import logging
import logging.handlers
import multiprocessing
import os
import os.path
import platform
import sys
import time

# Standard imports, alphabetical order
from itertools import cycle
from subprocess import PIPE, Popen
from typing import Any, Dict, List, Optional, Set

# Bundled modules
import python_one_password.caching as caching

# Setup logging
log = logging.getLogger(__name__)

# Define variables
# Get the home and present working directories
home_dir = os.path.expanduser("~")
pwd = os.getcwd()

# Used to source passwords from the shared password store
pass_mapping_file = home_dir + "/.password-store/.shared-configs/cloud-mappings.txt"


# General/shared functions


def contains_duplicates(this_list: List[str]) -> bool:
    """Determines if a list contains duplicate elements"""
    return this_list != list(dict.fromkeys(this_list))


def deduplicate_list(this_list: List[str]) -> List[str]:
    """De-duplicates a given list, preserving original order"""
    return list(dict.fromkeys(this_list))


def list_to_csv(this_list: List[str]) -> str:
    """Returns a comma separated string from a list object"""
    delim = ","
    return delim.join(list(map(str, this_list)))


def cred_update_refresh(
    update_commands: List[str], refresh_commands: List[str]
) -> None:
    """Modifies credential data and refreshes local metadata"""
    if not prompt("Commit these updates to the 1Password database?"):
        sys.exit(0)

    # Use timers to profile performance
    timer = start_timer()
    # Code must be single-threaded when making edits
    # TODO: implement a proper counter here to better progress
    log.info("Updating [%s] records:", len(update_commands))
    log_level = logging.getLogger().getEffectiveLevel()
    for command in update_commands:
        cmd_output = run_cmd_mp(command)
        if log_level == 10:
            log.debug(cmd_output)
        else:
            # Display progress on console when not debugging
            print(".", end="")
    stop_timer(timer)
    if log_level != 10:
        # Terminate progress line on console
        print("")

    # Refresh the local credential cache after updates

    # Use timers to profile performance
    timer = start_timer()
    updated_credential_db = []
    log.info("Multiprocessing call refreshing credential metadata")
    with multiprocessing.Pool() as pool:
        # Call the function for each item in parallel
        for raw_data in pool.map(run_cmd_mp, refresh_commands):
            log.debug(raw_data)
            updated_credential = json.loads(raw_data)
            updated_credential_db.append(updated_credential)
    stop_timer(timer)

    # Save vault detail dictionary to cache file
    caching.save_cache(updated_credential_db, "credentials")
    log.info("Credential metadata tags updated")


def tag_search_replace(
    credentials: List[Dict], search_string: str, replace_string: str
) -> None:
    """Searches credentials for a tag and replaces it with another"""
    log.debug(
        "\nSearching for: [%s]	Replacing with: [%s]\n", search_string, replace_string
    )

    update_commands = []
    refresh_commands = []
    matches = 0

    for credential in credentials:
        cred_id: str = credential["id"]
        name: str = credential["title"]
        try:
            tags: str = credential["tags"]
        except KeyError:
            # This credential has no tags
            # current_tags = []
            continue

        if search_string in tags:
            log.debug("Matched:	%s	%s	%s", cred_id, tags, name)
            matches += 1

            new_tags = []
            for tag in tags:
                new_tag = tag.replace(search_string, replace_string)
                new_tags.append(new_tag)

            # At this point duplicate tags are a concern; deduplicate them
            new_tags = deduplicate_list(new_tags)

            log.info("Updating:	%s	%s	%s", cred_id, new_tags, name)

            tags_string = list_to_csv(new_tags)

            update_commands.append("op item edit " + cred_id + " --tags " + tags_string)
            refresh_commands.append(
                "op item get " + cred_id + " --format=json --no-color"
            )

    log.info("Total matches: %s", matches)
    if matches > 0:
        cred_update_refresh(update_commands, refresh_commands)


def tags_update(
    credentials: List[Dict], tags: List[str], overwrite: bool, round_robin: bool
) -> None:
    """Performs tag operations on all currently selected credentials"""
    update_commands = []
    refresh_commands = []

    # Used only for round-robin allocations
    tags_cycle = cycle(tags)

    def next_tag():
        return next(tags_cycle)

    log.info("\n### Credentials: Future State ###\n")
    for credential in credentials:
        cred_id = credential["id"]
        name = credential["title"]
        current_tags: List[str] = []
        try:
            current_tags = credential["tags"]
        except KeyError:
            # Empty list already defined; no need to handle the error
            pass

        # When allocating tags, extract the next one from the list
        if round_robin:
            tags = [next_tag()]

        if not overwrite:
            # When NOT overwriting, add new tags to existing tags
            tags = tags + current_tags

        # De-duplicate list of tags; important when NOT overwriting
        # As we may be adding same tag may already exist...
        tags = deduplicate_list(tags)

        log.info("%s	%s	%s", cred_id, tags, name)

        if not tags:
            tags_string = '""'
        else:
            tags_string = list_to_csv(tags)

        update_commands.append("op item edit " + cred_id + " --tags " + tags_string)
        refresh_commands.append("op item get " + cred_id + " --format=json --no-color")

    cred_update_refresh(update_commands, refresh_commands)


def match_strings(ignore_case: bool, search_pattern: str, string: str) -> bool:
    """Returns true/false on string matching; optionally case-insensitive"""
    if ignore_case is True:
        if search_pattern.lower() in string.lower():
            return True
    else:
        if search_pattern in string:
            return True
    # Sub-string was not found in string
    return False


def credential_summary(
    credential_list: List[Dict], no_tags: bool, prompt_flag: bool
) -> None:
    """Displays a list/summary of the current working set of credentials"""

    # Prompt the user to review/display credentials
    # Note: can optionally be bypassed by setting prompt_flag to False
    if prompt_flag and not prompt("Review current credential state?"):
        return

    log.info("\n### Credentials: Current State ###\n")
    # Note: column output is tab separated
    for credential in credential_list:
        cred_id = credential["id"]
        name = credential["title"]
        # Tag display might make for messy output and take up excessive screen space
        # We therefore provide an option to suppress them in summary/output
        if no_tags:
            log.info("%s	%s", cred_id, name)
            continue
        # Not all credentials have tags, catch the exception
        try:
            tags = credential["tags"]
            log.info("%s	%s	%s", cred_id, tags, name)
        except KeyError:
            # Note: credentials without tags are padded with empty square brackets
            log.info("%s	[]	%s", cred_id, name)


def match_elements(
    ignore_case: bool, search_patterns: List[str], list_of_dictionaries: List[Dict]
) -> List[Dict]:
    """Returns a subset of elements matching a query from a list of dictionaries"""
    matched = []
    # Search individual term from a list of terms
    for search_pattern in search_patterns:
        # Create a counter to store searches matched for this specific query
        pattern_matches = 0
        for element in list_of_dictionaries:
            match = match_strings(ignore_case, search_pattern, str(element))
            # Need to prevent duplicates
            if match and element not in matched:
                pattern_matches += 1
                matched.append(element)
        log.info("Matching query:        [%s] %s", pattern_matches, search_pattern)
    return matched


def subtract_lists(
    primary_list: List[Dict], list_to_subtract: List[Dict]
) -> List[Dict]:
    """Subtracts one list of dictionaries from another based on id values"""
    primary_ids = []
    for dictionary in primary_list:
        primary_ids.append(dictionary["id"])
    log.debug("Identities: %s", primary_ids)
    subtract_ids = []
    for dictionary in list_to_subtract:
        subtract_ids.append(dictionary["id"])
    log.debug("Subtracting: %s", subtract_ids)
    remaining_ids = subtract_common_elements(primary_ids, subtract_ids)
    log.debug("Number of results: %s", len(remaining_ids))
    result = []
    for dictionary in primary_list:
        if dictionary["id"] in remaining_ids:
            result.append(dictionary)
    return result


def prompt(question: str) -> bool:
    """Displays a question; prompts for yes/no and returns a boolean"""
    while "Invalid selection":
        reply = str(input("\n" + question + " (y/n): ")).lower().strip()
        if reply[:1] == "y":
            return True
        if reply[:1] == "n":
            break
    return False


def filter_credentials(
    match: Optional[List[str]], reject: Optional[List[str]], ignore_case: bool
) -> List[Dict[str, Any]]:
    """Refines the current credential set through select/reject criteria"""
    if match == [] and reject == []:
        log.error("Error: provide at least one filter operation")
        log.error("Choose match, reject, or use both together")
        sys.exit(1)

    # List to hold filtered credentials, initially the complete database
    credentials = caching.load_cache("credentials")
    starting_number = len(credentials)

    if match:
        credentials = match_elements(ignore_case, match, credentials)
        log.info("Selected:              %s/%s", len(credentials), starting_number)
        # Print summary
        log.debug("\n### Selected Credentials ###\n")
        for credential in credentials:
            log.debug("%s	%s", credential["id"], credential["title"])

    if reject:
        rejected = match_elements(ignore_case, reject, credentials)
        log.info("Subsequently rejected: %s/%s", len(rejected), len(credentials))
        log.debug("\n### Rejected Credentials ###\n")
        for credential in rejected:
            log.debug("%s	%s", credential["id"], credential["title"])
        if len(rejected) != 0:
            credentials = subtract_lists(credentials, rejected)

    if credentials is None or len(credentials) == 0:
        log.info("\nNo results were returned for your filter(s)")
        sys.exit(1)
    else:
        log.info("\nCredentials now selected: %s", len(credentials))
    return credentials


def validate_filter_items_opts(
    match: Optional[List[str]], reject: Optional[List[str]]
) -> None:
    """Handles the options provided to the filter_items sub-command"""
    if match and reject:
        log.info("Both match and reject operations were requested...")
        log.warning("Note: match operations will run first, then reject")


def get_credentials_mp(vault: str) -> tuple[str, List[str]]:
    """Retrieves credential metadata JSON and returns as dictionary"""
    # Multiprocessing functions need logging setup
    log = logging.getLogger(__name__)
    cred_summ_cmd = "op item list --format=json --no-color --vault " + vault
    raw_data = run_cmd_mp(cred_summ_cmd)
    vault_credentials = json.loads(raw_data)
    log.debug("Credentials list:")
    log.debug(vault_credentials)
    return (vault, vault_credentials)


def import_credentials(vaults: Dict[str, str]) -> None:
    """Given a dictionary of vaults, populates the credential database(s)"""
    log.info("Importing credential metadata from 1Password database...")

    vault_credentials = []

    # Use timers to profile performance
    timer = start_timer()

    with multiprocessing.Pool() as pool:
        # Call the function for each item in parallel
        for vault, credentials in pool.map(get_credentials_mp, vaults):
            vault_creds_dictionary = {vault: credentials}
            vault_credentials.append(vault_creds_dictionary)

    stop_timer(timer)

    vaults_enumerated = len(vault_credentials)
    log.info("Credential data gathered for: %s vault(s)", vaults_enumerated)
    # Save vault detail dictionary to cache file
    caching.save_cache(vault_credentials, "vault_credentials")

    credentials = []
    # Copy individual credentials out into an abstract list
    for dictionary in vault_credentials:
        dict_credentials = list(dictionary.values())
        for credential_list in dict_credentials:
            for credential in credential_list:
                credentials.append(credential)

    # Print out total number of credentials in database
    log.info("Credential metadata records loaded: %s", len(credentials))
    # Save vault detail dictionary to cache file
    caching.save_cache(credentials, "credentials")


def validate_import_data_opts(
    match: Optional[List[str]], reject: Optional[List[str]]
) -> None:
    """Handles the options provided to the import_data sub-command"""
    log.debug("Validating command-line options/arguments")
    if reject and match != ["All"]:
        log.error("Match/reject options are mutually exclusive")
        sys.exit(1)


def get_vault_detail_mp(vault_dictionary: Dict) -> Dict[str, Any]:
    """Retrieves detailed vault metadata JSON and returns as dictionary"""
    # Multiprocessing functions need logging setup
    log = logging.getLogger(__name__)
    # Enumerate the details of each vault
    vault_id = vault_dictionary["id"]
    log.debug("Gathering data for vault: %s", vault_id)
    vault_detail_cmd = "op vault get " + vault_id + " --format=json --no-color"
    raw_data = run_cmd_mp(vault_detail_cmd)
    vault_detail = json.loads(raw_data)
    log.debug("get_vault_detail_mp returned data for: %s\n%s", vault_id, vault_detail)
    return vault_detail


# Functions to track elapsed time when performing bulk operations
def start_timer() -> float:
    """Starts a timer to track functions expected to do bulk work"""
    log.debug("Timer function started")
    return time.perf_counter()


def stop_timer(started: float) -> None:
    """Takes the time started and prints the elapsed time"""
    finished = time.perf_counter()
    elapsed = finished - started
    log.debug("Time taken in seconds: %s", elapsed)


def populate_vault_json(
    include: Optional[List[str]], exclude: Optional[List[str]]
) -> Dict[str, Any]:
    """Fetches additional vault metadata the summary doesn't provide"""

    # Handle optionals gracefully by defining empty lists
    if not include:
        include = []
    if not exclude:
        exclude = []

    log.info("Importing data from 1Password database...")
    vault_list_cmd = "op vault list --format=json --no-color"
    raw_data = run_cmd_mp(vault_list_cmd)
    vault_summary = json.loads(raw_data)
    log.debug("\nVaults summary:\n")
    log.debug("%s\n", vault_summary)
    # Save vault summary list to cache file
    caching.save_cache(vault_summary, "vault_summary")

    # Use timers to profile the performance of this code
    timer = start_timer()
    # TODO: Implement progress bar (more complex when multiprocessing)

    vaults_detail = {}
    with multiprocessing.Pool() as pool:
        # Call the function for each item in parallel
        for data in pool.map(get_vault_detail_mp, vault_summary):
            vault_id: str = data["id"]
            vault_name: str = data["name"]
            # Add items conditionally, based on include/exclude options
            if include == ["All"] and exclude == []:
                vaults_detail[vault_id] = data
            if include == ["All"] and exclude != []:
                # For convenience, include/exclude can match both name/id
                if vault_id not in exclude and vault_name not in exclude:
                    vaults_detail[vault_id] = data
            else:
                # Include was specified on the command-line
                if vault_id in include or vault_name in include:
                    vaults_detail[vault_id] = data
    stop_timer(timer)

    details_retrieved = len(vaults_detail)
    if details_retrieved == 0:
        log.warning("No vaults matched your request; no data imported")
        sys.exit(1)

    total_vaults = len(vault_summary)
    log.info("Total number of vaults: %s", total_vaults)

    # Save vault detail dictionary to cache file
    caching.save_cache(vaults_detail, "vaults_detail")

    # Integrity check; verify we collected detail records for all vaults
    if details_retrieved != total_vaults:
        log.info("Vaults imported into cache: %s", details_retrieved)

    return vaults_detail


def show_vault_summary(vaults_dictionary: Dict) -> None:
    """Prints a summary of vaults from a vaults dictionary"""
    log.info("\n########## Vault Summary ##########\n")
    log.info("ID				Name")
    for vault in vaults_dictionary.values():
        cred_id = vault["id"]
        name = vault["name"]
        log_string = cred_id + "	" + name
        log.info(log_string)
    log.info("")


def startup_tasks(debug: bool) -> None:
    """Invokes some common initialisation operations"""
    setup_logging(debug)
    op_login(debug)


def op_login(debug: bool) -> None:
    """Makes a connection to the 1Password database/servers"""
    # Documentation says the default timeout is 30 minutes
    run_cmd_mp("eval $(op signin)")

    if debug:
        # Gather some useful debugging information
        user_info = run_cmd_mp("op whoami")
        log.debug("\n%s", user_info)


def setup_logging(debug: bool) -> None:
    """Logging setup common to all sub-commands"""
    console_format = logging.Formatter("%(message)s")
    file_format = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")

    # Change root logger level from WARNING (default) to NOTSET
    # (makes sure all messages are delegated)
    logging.getLogger().setLevel(logging.NOTSET)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(console_format)
    console.setLevel(logging.INFO)

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("Logging level: " + str(logging.getLogger().getEffectiveLevel()))
        console.setLevel(logging.DEBUG)
        # Add second file handler, with level set to DEBUG
        debug_file = logging.handlers.RotatingFileHandler(filename="debug.log")
        debug_file.setFormatter(file_format)
        debug_file.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(debug_file)

    logging.getLogger().addHandler(console)

    # Default file log output with standard level INFO
    standard_file = logging.handlers.RotatingFileHandler(filename="standard.log")
    standard_file.setLevel(logging.INFO)
    standard_file.setFormatter(file_format)
    logging.getLogger().addHandler(standard_file)

    # Capture additional user/system information
    # Report CPUs available to Python multiprocessing
    log.debug("Processor cores available: %s", multiprocessing.cpu_count())
    log.debug("Python version: %s", platform.python_version())


def common_elements(first: List[str], second: List[str]) -> Set[str]:
    """Check for common elements in two lists"""
    return set(first) & set(second)


def subtract_common_elements(first: List[str], second: List[str]) -> Set[str]:
    """Remove common elements from two lists"""
    return set(first) - set(second)


# pylint: disable-next=R1710
def id_to_label(target: str, element: Dict[str, str]) -> str:
    """Returns the object name when given an id string"""
    if element["id"] == target:
        # TODO: return either element["name"] or element["id"]
        if element["name"]:
            return element["name"]
        if element["title"]:
            return element["title"]
    # If internal data structures are correct, the error below should never be thrown
    log.error("Function id_to_label failed to match requested string: %s", target)
    sys.exit(1)


# pylint: disable-next=R1710
def label_to_id(target: str, element: Dict[str, str]) -> str:
    """Returns an id string when given an object name/title"""
    # Vaults are named
    if element["name"] == target:
        return element["id"]
    # Credentials have titles
    if element["title"] == target:
        return element["id"]
    # If internal data structures are correct, the error below should never be thrown
    log.error("Function label_to_id failed to match requested string: %s", target)
    sys.exit(1)


def lookup_target(target: str, data: List[Dict]) -> tuple[str, str]:
    """Returns a tuple of element id/title from a single parameter"""
    # Vaults can either be specified as a key (id) or a value (name)
    # Credentials can either be specified as a key (id) or a value (title)
    # This function returns both properties when provided just one element
    for dictionary in data:
        if dictionary[target]:
            object_id = target
            label = id_to_label(object_id, dictionary)
            return (object_id, label)
        if target in dictionary.values():
            label = target
            object_id = label_to_id(label, dictionary)
            return (object_id, label)
    log.error("The specified vault id/label was not valid: %s", target)
    sys.exit(1)


def run_cmd_mp(shell_command: str) -> str:
    """Runs shell commands, returns stdout as text, handles errors"""
    # Multiprocessing functions need logging setup
    log = logging.getLogger(__name__)
    log.debug("Running shell command: %s", shell_command)
    with Popen(shell_command, stdout=PIPE, stderr=PIPE, shell=True) as command:
        # Capture the command exit status for error handling
        output, error = command.communicate(timeout=60)
        # Convert all command output into text
        command_output = output.decode("utf-8")
        command_error = error.decode("utf-8")

        # Create flag to capture error conditions
        errors = False

        if command.returncode == 127:
            separate_command_args = shell_command.split(" ", 1)
            root_command = separate_command_args.pop(0)
            log.info("A shell command was not found: %s", root_command)
            errors = True
        if command.returncode != 0:
            log.error("Error running command: %s", shell_command)

            log.info("Exit status: %s", command.returncode)
            # Provide some helpful hints based on the return code
            if command.returncode == (1, 6):
                log.info("Unlock/authenticate access to your password vault?")
                log.info("Try this command from a shell prompt: op signin")
            errors = True
        if command_output is None:
            log.warning("Shell command returned no text output: %s", shell_command)
            errors = True
        if errors:
            # We should always exit with error status if *any* shell commands fail
            log.error(command_error)
            log.error("Shell commands resulted in errors; exiting")
            sys.exit(1)

        # Without errors, return data to the calling site
        return command_output
