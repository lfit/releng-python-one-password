#!/Users/mwatkins/.pyenv/shims/python3
#!/usr/bin/python3

# -*- code: utf-8 -*-
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# COPYRIGHT
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

__author__ = "Matthew Watkins"

### Standard imports, alphabetical order
# from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import logging.handlers
import multiprocessing
import operator
import os
import os.path
import platform
import subprocess
import sys
import time
import typer
from typing import Optional
import caching

### TODO ###
# Potentially use the modules below to implement progress bars?
# from rich.progress import track
# from rich import progress


### Define command structure with typer module
try:
	# First step in defining CLI commands; requires typer module
	credential = typer.Typer()
except AttributeError as error:
	print("Check all Python modules/requirements are installed and available")
	print(error)
	sys.exit(1)


@credential.command()
def import_data(
	debug: bool = typer.Option(False, "--debug", "-d", show_default=False,
	                           help="Enable verbose debug output/logging"),
	include: Optional[list[str]] = typer.Option(
        ["All"], "--include", "-i", envvar="OP_VAULT_INC", help='Includes the specified vault(s) from processing'),
  	exclude: Optional[list[str]] = typer.Option(
  		None, "--exclude", "-e", envvar="OP_VAULT_EXC", help='Excludes the specified vault(s) from processing')
	):
	"""Import vaults and credentials from the 1Password database"""
	startup_tasks(debug)
	validate_import_data_opts(include, exclude)
	vaults_dictionary = populate_vault_json(include, exclude)
	show_vault_summary(vaults_dictionary)
	import_credentials(vaults_dictionary)


@credential.command()
def show_credentials(
	debug: bool = typer.Option(False, "--debug", "-d", show_default=False,
		help="Enable verbose debug output/logging"),
	no_tags: bool = typer.Option(False, "--no-tags", "-n",
		help="Hide metadata tags in credential summary/output")
	):
	"""Show credentials in current/filtered working set"""
	startup_tasks(debug)
	credential_summary(gl_credentials, no_tags)

@credential.command()
def filter_credentials(
	debug: bool = typer.Option(False, "--debug", "-d", show_default=False,
	    help="Enable verbose debug output/logging"),
	no_tags: bool = typer.Option(False, "--no-tags", "-n",
		help="Hide metadata tags in credential summary/output"),
	select: Optional[list[str]] = typer.Option(
	    None, "--select", "-s", help='Select/match credentials containing the specified text'),
	reject: Optional[list[str]] = typer.Option(
	    None, "--reject", "-r", help='Reject/exclude credentials containing the specified text'),
	ignore_case: bool = typer.Option(False, "--ignore-case", "-i", show_default=True,
		help="Ignore case when matching strings in credentials")
	):
	"""Filter selected credentials using select/reject options"""
	startup_tasks(debug)
	validate_filter_items_opts(select, reject)
	credentials = filter_credentials(select, reject, ignore_case)
	# Prompt for summary, prompt to update working set
	if yes_or_no("Display summary of selected credentials?"):
		credential_summary(credentials, no_tags)
	if yes_or_no("Update working credential set to selection?"):
		caching.save_cache(credentials, 'credentials')
	else:
		log.info("Select/reject did not modify credential database")

### Define variables

# Get the home and present working directories
home_dir = os.path.expanduser("~")
pwd = os.getcwd()

# Used to source passwords from the shared password store
pass_mapping_file = home_dir + '/.password-store/.shared-configs/cloud-mappings.txt'


### General/shared functions


def match_strings(ignore_case, search_pattern, string):
	"""Returns true/false on string matching; optionally case-insensitive"""
	if ignore_case == True:
		if search_pattern.lower() in string.lower():
			return True
	else:
		if search_pattern in string:
			return True
	# Sub-string was not found in string 
	return False


def credential_summary(list, no_tags):
	log.info("\n### Credentials ###\n")
	# Note: column output is tab separated
	for credential in list:
		id = credential['id']
		# Tag display might take up excessive screen space
		# Provide an option to suppress them in summary/output
		if no_tags:
			log.info("%s	%s", credential['id'], credential['title'])
		# Not all credentials have tags, catch the exception
		try:
			tags = credential['tags']
			log.info("%s	%s	%s", credential['id'], tags, credential['title'])
		except:
			# Note: credentials without tags are padded with empty square brackets
			log.info("%s	[]	%s", credential['id'], credential['title'])


def match_elements(ignore_case, search_patterns, list_of_dictionaries):
	"""Returns a subset of elements matching a query from a list of dictionaries"""
	matched = []
	# Search individual term from a list of terms
	for search_pattern in search_patterns:
		# Create a counter to store searches matched for this specific query
		pattern_matches = 0
		for element in list_of_dictionaries:
			match = match_strings(ignore_case, search_pattern, str(element))
			# Need to prevent duplicates
			if match and element not in matched:
				pattern_matches += 1
				matched.append(element)
		log.info("Matching query:        [%s] %s", pattern_matches, search_pattern)
	return matched


def subtract_lists(primary_list, list_to_subtract):
	"""Subtracts one list of dictionaries from another based on id values"""
	primary_ids = []
	for dictionary in primary_list:
		primary_ids.append(dictionary['id'])
	log.debug("Identities: %s", primary_ids)
	subtract_ids = []
	for dictionary in list_to_subtract:
		subtract_ids.append(dictionary['id'])
	log.debug("Subtracting: %s", subtract_ids)
	remaining_ids = subtract_common_elements(primary_ids, subtract_ids)
	log.debug("Number of results: %s", len(remaining_ids))
	result = []
	for dictionary in primary_list:
		if dictionary['id'] in remaining_ids:
			result.append(dictionary)
	return result


def yes_or_no(question):
	while "Invalid selection":
		reply = str(input("\n" + question + ' (y/n): ')).lower().strip()
		if reply[:1] == 'y':
			return True
		if reply[:1] == 'n':
			return False


def filter_credentials(select, reject, ignore_case):
	if select == [] and reject == []:
		log.error("Error: provide at least one filter operation")
		log.error("Choose select, reject, or use both together")
		sys.exit(1)

	# List to hold filtered credentials, initially the complete database
	credentials = caching.load_cache('credentials')		
	starting_number = len(credentials)
	
	if select:
		credentials = match_elements(ignore_case, select, credentials)
		log.info("Selected:              %s/%s", len(credentials), starting_number)
		# Print summary
		log.debug("\n### Selected Credentials ###\n")
		for credential in credentials:
			id = credential['id']
			log.debug("%s	%s", credential['id'], credential['title'])
			
	if reject:
		rejected = match_elements(ignore_case, reject, credentials)
		log.info("Subsequently rejected: %s/%s", len(rejected), len(credentials))
		log.debug("\n### Rejected Credentials ###\n")
		for credential in rejected:
			id = credential['id']
			log.debug("%s	%s", credential['id'], credential['title'])
		if len(rejected) != 0:
			credentials = subtract_lists(credentials, rejected)
		
	if credentials is None or len(credentials) == 0:
		log.info("\nNo results were returned for your filter(s)")
		sys.exit(1)
	else:
		log.info("\nCredentials now selected: %s", len(credentials))
	return credentials

def validate_filter_items_opts(include, exclude):
	"""Handles the options provided to the filter_items sub-command"""
	if len(include) != 0 and len(exclude) != 0:
		log.info("Both select and reject operations were requested...")
		log.warning("Note: select operations will run first, then reject")


def get_credentials_mp(vault):
	"""Retrieves credential metadata JSON and returns as dictionary"""
	try:
		log.debug("Multiprocessor-safe function validating logging environment")
	except NameError:
	    # NameError occurs with Python multiprocessing
		# Redefining the log target makes the function safe
	    log = logging.getLogger("app." + __name__)

	cred_summ_cmd = ('op item list --format=json --no-color --vault ' + vault)
	raw_data = run_cmd_mp(cred_summ_cmd)
	vault_credentials = json.loads(raw_data)
	log.debug("Credentials list:")
	log.debug(vault_credentials)
	return (vault, vault_credentials)


def import_credentials(vaults):
	"""Given a dictionary of vaults, populates the credential database(s)"""
	log.info("Importing credential metadata from 1Password database...")

	vault_credentials = []

	# Use timers to profile the performance of the code below
	timer = start_timer()
	with multiprocessing.Pool() as pool:
		# Call the function for each item in parallel
		for (vault, credentials) in pool.map(get_credentials_mp, vaults):
			vault_creds_dictionary = {vault: credentials}
			vault_credentials.append(vault_creds_dictionary)
	stop_timer(timer)

	vaults_enumerated = len(vault_credentials)
	log.info("Credential data gathered for: %s vault(s)", vaults_enumerated)
	# Save vault detail dictionary to cache file
	caching.save_cache(vault_credentials, 'vault_credentials')

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
	caching.save_cache(credentials, 'credentials')


def validate_import_data_opts(select, reject):
	"""Handles the options provided to the import_data sub-command"""
	log.debug("Validating command-line options/arguments")
	if len(reject) != 0 and select != ["All"]:
		log.error("Select/reject options are mutually exclusive")
		sys.exit(1)


def get_vault_detail_mp(vault_dictionary):
	"""Retrieves detailed vault metadata JSON and returns as dictionary"""
	try:
		log.debug("Multiprocessor-safe function validating logging environment")
	except NameError:
	    # NameError occurs with Python mutiprocessing
		# Redefining the log target makes the function safe
	    log = logging.getLogger("app." + __name__)
	# Enumerate the details of each vault
	vault_id = vault_dictionary['id']
	vault_name = vault_dictionary['name']
	# log.debug("Gathering data for: %s", vault_name)
	vault_detail_cmd = 'op vault get ' + vault_id + ' --format=json --no-color'
	raw_data = run_cmd_mp(vault_detail_cmd)
	vault_detail = json.loads(raw_data)
	# log.debug(vault_detail)
	return vault_detail


# Functions to track elapsed time when performing bulk operations
def start_timer():
	"""Starts a timer to track functions expected to do bulk work"""
	return (time.perf_counter())
def stop_timer(started):
	"""Takes the time started and prints the elapsed time"""
	finished = time.perf_counter()
	elapsed = (finished - started)
	log.debug("Time taken in seconds: %s", elapsed)


def populate_vault_json(include, exclude):
	"""Fetches vault metadata the regular list doesn't provide"""
	log.info("Importing data from 1Password database...")
	vault_list_cmd = 'op vault list --format=json --no-color'
	raw_data = run_cmd_mp(vault_list_cmd)
	vault_summary = json.loads(raw_data)
	log.debug("Vaults summary:")
	log.debug(vault_summary)
	# Save vault summary list to cache file
	caching.save_cache(vault_summary, 'vault_summary')

	# Use timers to profile the performance of this code
	timer = start_timer()
	# TODO: Implement progress bar (more complex when multiprocessing)
	
	vaults_detail = {}
	with multiprocessing.Pool() as pool:
		# Call the function for each item in parallel
		for data in pool.map(get_vault_detail_mp, vault_summary):
			vault_id = data['id']
			vault_name = data['name']
			# Add items conditionally, based on include/exclude options
			if include == ['All'] and exclude == []:
				vaults_detail[vault_id] = data
			if include == ['All'] and exclude != []:
				# For convenience, include/exclude can match both name/id 
				if vault_id not in exclude and vault_name not in exclude:
					vaults_detail[vault_id] = data
			else:
				# Include was specified on the command-line
				if vault_id in include or vault_name in include:
					vaults_detail[vault_id] = data
	stop_timer(timer)

	# Save vault detail dictionary to cache file
	caching.save_cache(vaults_detail, 'vaults_detail')

	total_vaults = len(vault_summary)
	log.info("Total number of vaults: %s", total_vaults)
	details_retrieved = len(vaults_detail)
	# Integrity check; verify we collected detail records for all vaults
	if details_retrieved != total_vaults:
		log.info("Vaults imported into cache: %s", details_retrieved)
	
	return vaults_detail


def show_vault_summary(vaults_dictionary):
	"""Prints a summary of vaults from a vaults dictionary"""
	log.info("########## Vault Summary ##########")
	log.info("Size	ID				Name")
	for vault in vaults_dictionary.values():
		# Vaults with no records will throw KeyError exception
		# The items key does not exist for them, so set it to zero!
		try:
			# Correction for vault['items'] counting credentials at index zero
			num_credentials = (vault['items'] + 1)
		except KeyError as error:
			num_credentials = 0
		id = vault['id']
		name = vault['name']
		log_string = (str(num_credentials) + "	" + id + "	" + name)
		log.info(log_string)


def startup_tasks(debug):
	setup_logging(debug)

	
def setup_logging(debug):
	"""Logging setup is common to all commands"""
	console_format = logging.Formatter('%(message)s')
	file_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
		
	# Change root logger level from WARNING (default) to NOTSET
	# (makes sure all messages are delegated)
	logging.getLogger().setLevel(logging.NOTSET)
	
	console = logging.StreamHandler(sys.stdout)
	console.setFormatter(console_format)
	console.setLevel(logging.INFO)
	
	if debug:
		console.setLevel(logging.DEBUG)
		# Add second file handler, with level set to DEBUG
		debug_file = logging.handlers.RotatingFileHandler(filename='debug.log')
		debug_file.setFormatter(file_format)
		debug_file.setLevel(logging.DEBUG)
		logging.getLogger().addHandler(debug_file)

	logging.getLogger().addHandler(console)

    # Default file log output with standard level INFO
	standard_file = logging.handlers.RotatingFileHandler(filename='standard.log')
	standard_file.setLevel(logging.INFO)
	standard_file.setFormatter(file_format)
	logging.getLogger().addHandler(standard_file)
	
	# Capture additional user/system information
	# Report CPUs available to Python multiprocessing
	log.debug("Processor cores available: %s", multiprocessing.cpu_count())
	log.debug("Python version: %s", platform.python_version())
	# Forces a 1Password login/authentication event
	user_info = run_cmd_mp("op whoami")
	log.debug(user_info)

### TODO ### Currently unused, remove later?
def common_elements(a, b):
    """Check for common elements in two lists"""
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        return True
    else:
        return False
### TODO ### Currently unused, remove later?
def subtract_common_elements(a, b):
	"""Check for common elements in two lists"""
	a_set = set(a)
	b_set = set(b)
	if (a_set & b_set):
		return (a_set - b_set)


# A pair of utility functions to lookup vault information
def id_to_label(id, list):
	for element in list:
		if vault['id'] == id:
			return(vault['name'])
def label_to_id(label, list):
    for element in list:
        if element['name'] == label:
            return (element['id'])
        elif element['title'] == label:
            return (element['id'])


def lookup_target(target, data):
	"""Returns a tuple of element id/title from a single parameter"""
	# Vaults can either be specified as a key (id) or a value (name)
	# Credentials can either be specified as a key (id) or a value (title)
	# This function returns both properties when provided just one element
	if target in data:
		id = target
		label = id_to_label(id, data)
		return (id, label)
	elif target in data.values():
		label = target
		id = label_to_id(label, data)
		return (id, label)
	else:
		log.error("The specified vault id/label was not valid: " + target)
		sys.exit(1)    


def run_cmd_mp(shell_command):
    """Runs shell commands, returns stdout as text, handles errors"""
    try:
        log.debug("Multiprocessor-safe function validating logging environment")
    except NameError:
	    # NameError occurs with Python mutiprocessing
		# Redefining the log target makes the function safe
	    log = logging.getLogger("app." + __name__)

    # Define a flag to indicate error conditions
    errors = False

    log.debug("Running shell command: %s", shell_command)
    command = subprocess.Popen(
        shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # Convert all command output into text
    command_output = command.stdout.read().decode("utf-8")
    command_error = command.stdout.read().decode("utf-8")
    # Close the file handles, they will stay open "forever" otherwise.
    command.stdout.close()
    command.stderr.close()
    # Capture the command exit status for error handling
    command.communicate()

    if command.returncode == 127:
        separate_command_args = shell_command.split(' ', 1)
        root_command = separate_command_args.pop(0)
        log.info("A shell command was not found: %s", root_command)
        errors = True
    if command.returncode != 0:
        log.info("Command invocation exit status: %s", command.returncode)
	# Provide some helpful hints based on the return code
        if command.returncode == 1 or command.returncode == 6:
            log.info("Unlock/authenticate access to your password vault?")
            log.info("Try this command from a shell prompt: op signin")
        errors = True
    if command_output is None:
        log.info("A shell command returned no text output: %s", shell_command)
        errors = True
    if errors:
        # We should always exit with error status if *any* shell commands fail
        log.info("Shell commands resulted in errors; exiting")
        sys.exit(1)

	# Without errors, return data to the calling site
    return (command_output)


### Main script entry point
if __name__ == "__main__":
	log = logging.getLogger("app." + __name__)
	credential()