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
from enum import Enum
import json
import logging
import os
import os.path


### Configure logging ###

log = logging.getLogger(__name__)


### JSON cache files ###

class DataStore(Enum):
	# Define local JSON data filenames
	vault_summary = 'vault.summary.metadata.json'
	vaults_detail = 'vault.detailed.metadata.json'
	vault_credentials = 'vault.credentials.metadata.json'
	credentials = 'credentials.metadata.json'


### File/caching operations ###

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


def validate_cache():
	"""Checks metadata and only updates the required objects in the local cache"""
	# Check metadata modification times and version numbers; selectively reload data
	pass


def check_file_age(file):
	"""Returns the age of a file on disk in seconds"""
	return age_in_seconds(os.path.getmtime(file))


def load_cache(data_store):
	"""Loads data from the filesystem and returns the JSON"""	
	data_store = ("DataStore." + data_store)
	log.debug("Request to load records from cache: %s", data_store)
	for store_name in DataStore:
		if data_store == str(store_name):
			data = load_json_file(store_name.value)
			log.info("Loaded cached JSON metadata: [%s] records", len(data))
			log.debug(data)
			return data
	log.error("The requested cache does not exist: %s", data_store)
	sys.exit(1)


def save_cache(json_data, data_store):
	"""Saves JSON data to the filesystem"""
	log.debug("Saving [%s] records to cache: %s", len(json_data), data_store)
	data_store = ("DataStore." + data_store)
	for store_name in DataStore:
		if data_store == str(store_name):
			save_json_file(json_data, store_name.value)				
			return
	log.error("The requested cache does not exist: %s", data_store)
	sys.exit(1)


### TODO ###
# Implement cache validity/checking
def check_cache():
	"""Checks the age of the files in the local cache"""
	
	### Temporarily set high; local cache never expires ###
	cache_validity = 999999
	log.debug("Cache lifetime/expiry set to: %s seconds", cache_validity)
	if os.path.isfile(gl_vaults_detail_db):
		age = check_file_age(gl_vaults_detail_db)
		if age > cache_validity:
			return False
		else:
			# Load cached data from disk
			old_load_cache()
			return True
	else:
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