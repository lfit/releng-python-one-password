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

### Standard imports, alphabetical order ###
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import os
import os.path
import sys

### Configure logging ###
log = logging.getLogger(__name__)


### JSON cache files ###
class DataStore(Enum):
	# Define local JSON data filenames
	vault_summary = 'vault.summary.metadata.json'
	vaults_detail = 'vault.detailed.metadata.json'
	vault_credentials = 'vault.credentials.metadata.json'
	credentials = 'credentials.metadata.json'


### Set cache validity/age
cache_validity = 999999


### File/caching operations ###

def age_in_seconds(mtime):
	"""Return the age in seconds of a given mtime value"""
	now = datetime.now()
	then = datetime.fromtimestamp(mtime)
	return (now-then).total_seconds()


def load_json_file(filename):
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


def save_json_file(json_data, filename):
	"""Saves a JSON data object to disk"""
	try:
		with open(filename, "w") as write_file:
			json.dump(json_data, write_file)
			log.debug("JSON written to file: %s", filename)
	except:
		log.error("Error writing JSON to file: %s", filename)
		sys.exit(1)
	# Clean up afterwards
	write_file.close()


def check_file_age(file):
	"""Returns the age of a file on disk in seconds"""
	return age_in_seconds(os.path.getmtime(file))


def lookup_filename(data_store):
	"""Returns the filename of a given data store"""
	data_store = ("DataStore." + data_store)
	for store_name in DataStore:
		if data_store == str(store_name):
			return store_name.value
	log.error("The requested cache does not exist: %s", data_store)
	sys.exit(1)


def load_cache(data_store):
	"""Loads data from the filesystem and returns the JSON"""
	log.debug("Request to load records from cache: %s", data_store)
	filename = lookup_filename(data_store)
	
	# Check if the existing cached JSON data is valid
	if validate_cache(filename) == False:
		refresh_cache()

	data = load_json_file(filename)
	log.info("Loaded cached JSON metadata: [%s] records", len(data))
	log.debug(data)
	return data


def save_cache(json_data, data_store):
	"""Saves JSON data to the filesystem"""
	log.info("Saving [%s] records to cache: %s", len(json_data), data_store)
	filename = lookup_filename(data_store)
	save_json_file(json_data, filename)				
	return


### TODO ###
# Implement cache validity/checking
def validate_cache(filename):
	"""Checks the age of the files in the local cache"""
	### Temporarily set high; local cache effectively never expires ###
	log.debug("Cache lifetime/expiry is: %s seconds", cache_validity)
	if os.path.isfile(filename):
		age = check_file_age(filename)
		if age < cache_validity:
			log.debug("Cache passed validity check")
			return True
		log.debug("Cache failed validity check")
		return False


### TODO ###
# Implement cache validity/checking
def refresh_cache():
	# Currently send an error back to the user for manual action
	# The intention is this will later will call validate_cache()
	log.error("The local cache file(s) are invalid or could not be loaded")
	log.error("Use import-data to load credentials from the required vault(s)")
	sys.exit(1)


### File/Caching Operations ###