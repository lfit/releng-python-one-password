#!/Users/mwatkins/.pyenv/shims/python3
#!/usr/bin/python3

# -*- code: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
##############################################################################
# Copyright (c) 2017 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

__author__ = "Matthew Watkins"

### Standard imports, alphabetical order
from datetime import datetime, timedelta
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
def filter_items(
	debug: bool = typer.Option(False, "--debug", "-d", show_default=False,
	    help="Enable verbose debug output/logging"),
	include: Optional[list[str]] = typer.Option(
	    None, "--select", "-s", help='Select/match credentials containing the specified text'),
	exclude: Optional[list[str]] = typer.Option(
	    None, "--reject", "-r", help='Reject/exclude credentials containing the specified text'),
	ignore_case: bool = typer.Option(False, "--ignore-case", "-i", show_default=True,
		help="Ignore case when matching strings in credentials")
	):
	"""Filter selected credentials using include/exclude options"""
	startup_tasks(debug)
	validate_filter_items_opts(include, exclude)
	check_cache()
	filter_credential_db(include, exclude, ignore_case)


### Define variables

# Get the home and present working directories
home_dir = os.path.expanduser("~")
pwd = os.getcwd()

# Used to source passwords from the shared password store
pass_mapping_file = home_dir + '/.password-store/.shared-configs/cloud-mappings.txt'


### Global data objects

gl_vault_list = []
gl_vault_list_db = "vault.summary.metadata.json"
gl_vaults_detail = {}
gl_vaults_detail_db = "vault.detailed.metadata.json"
gl_vault_credentials = []
gl_vault_credentials_db = "vault.credentials.metadata.json"
gl_credentials = []
gl_credentials_db = "filtered.credentials.metadata.json"


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

def match_elements(ignore_case, search_patterns, list_of_dictionaries):
	"""Returns a subset of elements matching a query from a list of dictionaries"""
	matched = []
	# Search individual term from a list of terms
	for search_pattern in search_patterns:
		# Create a counter to store searches matched for this specific query
		pattern_matches = 0
		for element in list_of_dictionaries:
			match = match_strings(ignore_case, search_pattern, str(element))
			if match:
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


def filter_credential_db(select, reject, ignore_case):
	if select == [] and reject == []:
		log.error("Error: at least one filter operation must be provided")
		log.error("Choose either include/exclude options or use both")
		sys.exit(1)

	# List to hold filtered credentials, initially the complete database
	filtered_credentials = gl_credentials
	
	# Create lists to hold included/excluded credentials
	if select:
		selected = match_elements(ignore_case, select, gl_credentials)
		log.info("Selected:              %s/%s", len(selected), len(gl_credentials))
		filtered_credentials = selected

	if reject:
		rejected = match_elements(ignore_case, reject, filtered_credentials)
		log.info("Subsequently rejected: %s/%s", len(rejected), len(filtered_credentials))

	# Show a summary of matches to select/reject
	if select:
		# Print summary
		log.debug("\n### Selected Credentials ###\n")
		for credential in selected:
			id = credential['id']
			log.debug("%s	%s", credential['id'], credential['title'])
			
	if reject:
		log.debug("\n### Rejected Credentials ###\n")
		for credential in rejected:
			id = credential['id']
			log.debug("%s	%s", credential['id'], credential['title'])
	
	# Only perform subtraction if reject operations were given
	if rejected:
		filtered_credentials = subtract_lists(filtered_credentials, rejected)
		
	if filtered_credentials is None or len(filtered_credentials) == 0:
		log.info("\nNo results were returned for your filter(s)")
		sys.exit(1)
	else:
		log.info("\nCredentials now selected: %s", len(filtered_credentials))
		
	# Prompt for summary, prompt to update working set
	if yes_or_no("Display summary of selected credentials?"):
		log.info("\n### Credentials ###\n")
		for credential in filtered_credentials:
			id = credential['id']
			log.info("%s	%s", credential['id'], credential['title'])
	if yes_or_no("Update working credential set to selection?"):
		save_json_file(gl_credentials, gl_credentials_db)
	else:
		log.info("Select/reject did not modify credential database")

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
	    # NameError occurs with Python mutiprocessing
		# Redefining the log target makes the function safe
	    log = logging.getLogger("app." + __name__)

	cred_summ_cmd = ('op item list --format=json --no-color --vault ' + vault)
	raw_data = run_cmd_mp(cred_summ_cmd)
	vault_credentials = json.loads(raw_data)
	log.debug("Credentials list:")
	log.debug(vault_credentials)
	return (vault, vault_credentials)


def extract_elements(list_of_dictionaries):
	
	# Copy individual credentials out into an abstract list
	#for dictionary in gl_vault_credentials:
	#	credentials = list(dictionary.values())
	#	for credential_list in credentials:
	#		for credential in credential_list:
	#			gl_credentials.append(credential)
				
	# Copy individual credentials out into an abstract list
	for dictionary in list_of_dictionaries:
		element = list(dictionary.values())
		for credential_list in credentials:
			for credential in credential_list:
				gl_credentials.append(credential)


def import_credentials(vaults):
	"""Given a dictionary of vaults, populates the credential database(s)"""
	log.info("Importing credential metadata from 1Password database...")

	# Use timers to profile the performance of this code
	timer = start_timer()
	with multiprocessing.Pool() as pool:
		# Call the function for each item in parallel
		for (vault, credentials) in pool.map(get_credentials_mp, vaults):
			vault_creds_dictionary = {vault: credentials}
			gl_vault_credentials.append(vault_creds_dictionary)
	stop_timer(timer)

	vaults_enumerated = len(gl_vault_credentials)
	log.info("Credential data gathered for: %s vault(s)", vaults_enumerated)
	# Save vault detail dictionary to cache file
	save_json_file(gl_vault_credentials, gl_vault_credentials_db)

	# Copy individual credentials out into an abstract list
	for dictionary in gl_vault_credentials:
		credentials = list(dictionary.values())
		for credential_list in credentials:
			for credential in credential_list:
				gl_credentials.append(credential)
	
	# Print out total number of credentials in database
	log.info("Credential metadata records loaded: %s", len(gl_credentials))
	# Save vault detail dictionary to cache file
	save_json_file(gl_credentials, gl_credentials_db)

def validate_import_data_opts(include, exclude):
	"""Handles the options provided to the import_data sub-command"""
	log.debug("Validating command-line options/arguments")
	if len(exclude) != 0 and include != ["All"]:
		log.error("Include/exclude options are mutually exclusive")
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
	vault_list = json.loads(raw_data)
	log.debug("Vaults list:")
	log.debug(vault_list)
	# Save vault summary list to cache file
	save_json_file(vault_list, gl_vault_list_db)

	# Use timers to profile the performance of this code
	timer = start_timer()
	# TODO: Implement progress bar (more complex when multiprocessing)
	
	vaults_detail = {}
	with multiprocessing.Pool() as pool:
		# Call the function for each item in parallel
		for data in pool.map(get_vault_detail_mp, vault_list):
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
	save_json_file(vaults_detail, gl_vaults_detail_db)

	total_vaults = len(vault_list)
	log.info("Total number of vaults: %s", total_vaults)
	details_retrieved = len(vaults_detail)
	# Integrity check; verify we collected detail records for all vaults
	if details_retrieved != total_vaults:
		log.info("Vaults imported into cache: %s", details_retrieved)
	
	return vaults_detail


def load_cache():
	"""Loads all cached JSON data structures from disk"""
	global gl_vault_list
	global gl_vault_list_db
	global gl_vaults_detail
	global gl_vaults_detail_db
	global gl_vault_credentials
	global gl_vault_credentials_db
	global gl_credentials
	global gl_credentials_db

	gl_vault_list = read_json_file(gl_vault_list_db)
	log.debug(gl_vault_list_db)
	gl_vaults_detail = read_json_file(gl_vaults_detail_db)
	log.debug(gl_vaults_detail)
	gl_vault_credentials = read_json_file(gl_vault_credentials_db)
	log.debug(gl_vault_credentials)
	gl_credentials = read_json_file(gl_credentials_db)
	log.debug(gl_credentials)

	log.info("Loaded cached vault/credential information")
	log.debug("Vaults in database:   %s", len(gl_vault_list))
	log.debug("Vaults imported:      %s", len(gl_vaults_detail))
	# Iterate over vault credentials
	vault_credentials = 0
	for dictionary in gl_vault_credentials:
		# Vault id is dictionary key
		for vault_id in dictionary.keys():
			credentials = dictionary[vault_id]
			vault_credentials += len(credentials)
	log.debug("Credentials imported: %s", vault_credentials)
	# log.debug("Filtered credentials: %s", len(gl_credentials))


def show_vault_summary(vaults_dictionary):
	"""Prints a summary of vaults from a vaults dictionary"""
	log.info("########## Vault Summary ##########")
	log.info("Size	ID				Name")
	for vault in vaults_dictionary.values():
		# Vaults with no records will throw KeyError exception
		# The items key does not exist for them, so set it to zero!
		try:
			credentials = vault['items']
		except KeyError as error:
			credentials = 0
		id = vault['id']
		name = vault['name']
		log_string = (str(credentials) + "	" + id + "	" + name)
		log.info(log_string)


def startup_tasks(debug):
	"""Common startup tasks to all commands"""
	# Change root logger level from WARNING (default) to NOTSET in order for all messages to be delegated.
	logging.getLogger().setLevel(logging.NOTSET)

	# Add console handler, with variable level based on debugging flag
	console = logging.StreamHandler(sys.stdout)
	if debug:
		console.setLevel(logging.DEBUG)
	else:
		console.setLevel(logging.INFO)
	formater = logging.Formatter('%(message)s')
	console.setFormatter(formater)
	logging.getLogger().addHandler(console)

    # Default file log output with standard level INFO
	info = logging.handlers.RotatingFileHandler(filename='standard.log')
	info.setLevel(logging.INFO)
	file_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
	info.setFormatter(file_format)
	logging.getLogger().addHandler(info)

	# Add second file handler, with level DEBUG
	debug = logging.handlers.RotatingFileHandler(filename='debug.log')
	debug.setLevel(logging.DEBUG)
	file_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
	debug.setFormatter(file_format)
	logging.getLogger().addHandler(debug)

	# Report CPUs available to Python multiprocessing
	log.debug("Processor cores available: %s", multiprocessing.cpu_count())

	# Add user/account information to debug output only
	user_info = run_cmd_mp("op whoami")
	log.debug(user_info)


def save_json_file(json_data, filename):
	"""Saves a JSON data object to disk"""
	try:
		with open(filename, "w") as write_file:
			json.dump(json_data, write_file)
			log.info("JSON written to cache: %s", filename)
	except:
		log.error("Error writing JSON to file: %s", filename)
		sys.exit(1)
	# Clean up afterwards
	write_file.close()


def read_json_file(filename):
	"""Returns JSON data object from a given file"""
	try:
		with open(filename) as open_file:
			data = json.loads(open_file.read())
			log.debug("JSON read from file: %s", filename)
	except Exception as error:
		log.error("Error reading JSON from file: %s", filename)
		log.error(error)
		sys.exit(1)
	open_file.close()
	return data


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


def age_in_seconds(mtime):
	"""Return the age in seconds of a given mtime value"""
	now = datetime.now()
	then = datetime.fromtimestamp(mtime)
	return (now-then).total_seconds()


### TODO ###
def validate_cache():
	"""Not used yet; vault detail could be used to establish cache validity"""
	# Compare the metadata from a summary query with that in the cache
	# Check vault last modified dates, reload credential database if necessary
	pass


def check_cache():
	"""Not used yet; will be called by credential management sub-commands"""
	# Define the cache validity in seconds
	# cache_validity = 1200
	### TODO ### Implement proper cache validity checking
	### Temporarily assume local cache never expires/invalid ###
	cache_validity = 999999
	log.debug("Cache lifetime/expiry set to: %s seconds", cache_validity)
	if os.path.isfile(gl_vaults_detail_db):
		age = age_in_seconds(os.path.getmtime(gl_vaults_detail_db))
		if age > cache_validity:
			return False
		else:
			# Load cached data from disk
			load_cache()
			return True
	else:
		return False


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