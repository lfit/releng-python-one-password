#!/Users/mwatkins/.pyenv/shims/python3

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

import sys
import logging
import logging.handlers
import click
import os
import platform
import subprocess
import sys
from datetime import datetime, timedelta

# Handle external Python modules carefully
try:
    import click
except ImportError:
    sys.exit("Could not import external module: click")


### Define variables
    
# Get the home and present working directories
home_dir = os.path.expanduser("~")
pwd = os.getcwd()

# Used to source passwords from the shared password store
pass_mapping_file = home_dir + '/.password-store/.shared-configs/cloud-mappings.txt'
### Define keys/values we do NOT want to process ###
exclude_vaults_dictionary = {'nmyk5ccmeglgmu4l7vqgeuk3ua': 'Private', 'tn4y2cveivccdpokn5zkzglmaq': 'My Linux Foundation'}

### Commands used for vault operations ###
vault_list_cmd = "op vault ls"
# Syntax:       op item list --vault [vault name]
vault_content_cmd = "op item list --vault "

### Numerical variables used for reporting purposes ###
total_vaults = 0
vaults_to_process = 0
vaults_excluded = 0
vaults_processed = 0

### Global data objects
vault_metadata = {}
vault_elements = {}


### Setup/define command structure

@click.group()
@click.option('--debug', '-d', required=False, is_flag=True, default=False, help='Debug/verbose output')
def cli(debug):
    if debug:
        click.echo("Logging level set to debug/verbose")
        setup_logging(True)
    else:
        setup_logging(False)
        
@cli.command()
@click.option('--vault', '-v', required=False, help='Limit processing to a single vault')
def stats(vault):

    ### stats command, main entry point ###        
    log.info("### Processing 1Password Vaults ###")
    
    vaults_dictionary = retrieve_vault_list()
    total_vaults = vaults_dictionary.keys()
    log.info("Number of vaults in database: %s", len(total_vaults))
    
    # Remove any vaults that need to be excluded
    vaults_dictionary = filter_vaults(vaults_dictionary)
    vaults_to_process = vaults_dictionary.keys()
    vaults_excluded = total_vaults - vaults_to_process
    log.info("Number of vaults excluded: %s", len(vaults_excluded))
    log.info("Number of vaults to process: %s", len(vaults_dictionary))
    
    if vault:
        if vault in vaults_dictionary.items().keys OR if vault in vaults_dictionary.items().values:
            log.info('Querying vault: ' + vault)
        else:
            log.error("The specified vault id/name was not valid")
            sys.exit(1)
    else:
        
        
    log.info('Querying all vaults')
    for id, vault_name in vaults_dictionary.items():
        log.info("Processing Vault: %s", vault_name)
        enumerate_vault_contents(vault_name)
    
    ### Provide useful metadata/report prior to exit ###
    
    ### TODO ###
    
    log.info ("### Script Completed ###")


### General functions

def setup_logging(verbose):
    # Change root logger level from WARNING (default) to NOTSET in order for all messages to be delegated.
    logging.getLogger().setLevel(logging.NOTSET)
    
    # Add console handler, with variable level based on debugging flag
    console = logging.StreamHandler(sys.stdout)
    if verbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    formater = logging.Formatter('%(message)s')
    console.setFormatter(formater)
    logging.getLogger().addHandler(console)
    
    # Add file handler, with level INFO
    info = logging.handlers.RotatingFileHandler(filename='standard.log')
    info.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    info.setFormatter(file_format)
    logging.getLogger().addHandler(info)
    
    if verbose:
        # Add file handler, with level DEBUG
        debug = logging.handlers.RotatingFileHandler(filename='debug.log')
        debug.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
        debug.setFormatter(file_format)
        logging.getLogger().addHandler(debug)
    
    # log = logging.getLogger("app." + __name__)


def run_command(shell_command):
    """Runs shell commands, returns stdout as text, handles errors"""

    # Define a flag to indicate error conditions
    errors = False
    
    log.debug("Running command: " + vault_list_cmd + "")
    
    command = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
    # Convert all command output into text
    command_output = command.stdout.read().decode("utf-8")
    command_error = command.stdout.read().decode("utf-8")
    # Capture the command exit status for error handling    

    # Close the file handles, they will stay open "forever" otherwise.
    command.stdout.close()
    command.stderr.close()
    
    command.communicate()
    
    if command.returncode == 127:
        separate_command_args = shell_command.split(' ', 1)
        root_command = separate_command_args.pop(0)
        log.info("A shell command was not found: " + root_command)
        errors = True
    
    if command.returncode != 0:
        log.info("Command invocation exit status:", command.returncode)
        errors = True
    
    if command_output is None:
        log.info("A shell command returned no text output: " + shell_command)
        errors = True
    
    if errors:
        # We should always exit with error status if *any* shell commands fail
        log.info("Shell commands resulted in errors; exiting")
        exit(1)

    return(command_output)


def retrieve_vault_list():
    # Returns a dictionary of vaults from the 1Password database
    output = run_command(vault_list_cmd)
    log.info(output)
    # Strip the first line, which is the column header NOT data
    output = output.split('\n', 1)[1]
    # Define a dictionary to hold the data
    vaults_dictionary = {}
    
    # Process each line of output, adding dictionary elements
    for row in output.split("\n"):
        # Process until last empty row
        if row == '':
            break
        fields = row.split(' ', 1)
        key = fields.pop(0)
        value = fields[0].lstrip()
        vaults_dictionary[key] = value
        log.debug("Key: " + key + " Value: " + value)

    log.debug("Python Dictionary created from 1Password Vault:")
    log.debug(vaults_dictionary)
    return vaults_dictionary
    
    
def filter_vaults(unfiltered_vaults):
    # Removes vaults that need to be excluded from scan 
    filtered_vaults = dict(set(unfiltered_vaults.items()) - set(exclude_vaults_dictionary.items()))
    log.debug("Excluded vaults: ")
    for excluded_vault in exclude_vaults_dictionary.values():
        log.debug("    " + excluded_vault)
    return filtered_vaults
    
    
def enumerate_vault_contents(vault_name):
    cmd_string = (vault_content_cmd + '"' + vault_name + '"')
    log.debug("Running command: " + cmd_string + "")
    cmdpipe = subprocess.Popen(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # Command convert command output into text
    output = cmdpipe.stdout.read().decode("utf-8")
    # Close the file handles, they will stay open "forever" otherwise.
    cmdpipe.stdout.close()
    cmdpipe.stderr.close()
    
    # Process until last empty row
    if output == '':
        log.debug("No output data to process for query")
        return

    # Display the full vault content when debugging, including column headers
    log.debug(output)
    
    # Extract the raw data by removing the column headers
    vault_content = output.split('\n', 1)[1]


### Main script entry point ###

if __name__ == '__main__':
    log = logging.getLogger("app." + __name__)
    cli()
