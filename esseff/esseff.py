#!/usr/bin/python

"""esseff.esseff: provides entry point main()."""


__version__ = "0.0.1"

import sys
import os
import os.path
import subprocess
import re
import json
import ConfigParser
import hashlib
import tempfile
from string import Template
import yaml
import boto3

NODE_LAMBDA_TEMPLATE = """
console.log('starting update_fleet function');

const AWS = require("aws-sdk");
const SFN = new AWS.StepFunctions()

exports.handle = function(e, ctx, cb) {

}
"""

def get_client(region, access_key, secret_key):
    sfn_client = boto3.client(
        'stepfunctions',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    return sfn_client

def load_all_machines(sfn_client):
    machines = []

    token = "blah"

    while token:
        response = sfn_client.list_state_machines(maxResults=1000)
        machines += response['stateMachines']
        if 'nextToken' in response:
            token = response['nextToken']
        else:
            token = None

    return machines

def list_machines_by_name(sfn_client, name):
    machines = load_all_machines(sfn_client)

    machines_by_name = {}

    for machine in machines:
        if re.match("^" + name + "-[0-9]+$", machine['name']):
            machines_by_name[machine['name']] = machine

    return machines_by_name

def get_latest_machine(sfn_client, state_machine_name):
    machines = list_machines_by_name(sfn_client, state_machine_name)

    latest_machine = None
    max_ver = -1

    for name in machines:
        cur_ver = int(name.rsplit('-', 1)[1])

        if cur_ver > max_ver:
            max_ver = cur_ver
            latest_machine = machines[name]

    # load all data for this machine
    if latest_machine:
        latest_machine = sfn_client.describe_state_machine(stateMachineArn=latest_machine['stateMachineArn'])

    return latest_machine

def get_next_version_name(state_machine_name):
    cur_name = state_machine_name.rsplit('-', 1)[0]
    cur_ver = int(state_machine_name.rsplit('-', 1)[1])
    
    return "{}-{}".format(cur_name, cur_ver + 1)

def get_config_value(config, section_name, config_key, default=None):
    if not config or not config.has_section(section_name) or not config.has_option(section_name, config_key):
        return default

    value = config.get(section_name, config_key)

    if not value:
        return default

    return value

def get_flattened_config_value(global_config, config, section_name, config_key, default=None):
    fallback_value = get_config_value(global_config, section_name, config_key, default)
    return get_config_value(config, section_name, config_key, fallback_value)

def compare_defs(previous_def, current_def):
    previous_hash = hashlib.md5(previous_def.encode())
    current_hash = hashlib.md5(current_def.encode())
    return previous_hash.hexdigest() == current_hash.hexdigest()

def execute_statelint(path, file):
    output = subprocess.check_output(["statelint", os.path.join(path, file)])

    if output:
        print output
        return False

    return True


def lint_state_machines(path):
    overall_lint_success = True

    for filename in os.listdir(path):
        if filename.endswith(".json") or filename.endswith(".yml") or filename.endswith(".yaml"):
            temp_file = None

            print "Linting {} ...".format(filename)

            if filename.endswith(".yml") or filename.endswith(".yaml"):
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(json.dumps(yaml.load(open(os.path.join(path, filename), 'r').read()), indent=4))
                temp_file.close()
                filename = temp_file.name

            lint_ok = execute_statelint(path, filename)

            if temp_file:
                os.remove(filename)

            if not lint_ok:
                overall_lint_success = False

    return overall_lint_success

def deploy_state_machines(path):

    global_config_file = os.path.join(path, "esseff.config")

    global_config = None

    if os.path.exists(global_config_file):
        global_config = ConfigParser.RawConfigParser()
        global_config.read(global_config_file)

    for filename in os.listdir(path):
        if filename.endswith(".json") or filename.endswith(".yml") or filename.endswith(".yaml"):
            print "Deploying: {}".format(filename)
            state_machine_name = filename.rsplit('.', 1)[0]

            config_file = os.path.join(path, state_machine_name + ".config")
            config = None

            if os.path.exists(config_file):
                config = ConfigParser.RawConfigParser()
                config.read(config_file)

            access_key = get_flattened_config_value(global_config, config, 'AWS', 'aws_access_key_id')
            secret_key = get_flattened_config_value(global_config, config, 'AWS', 'aws_secret_access_key')
            region = get_flattened_config_value(global_config, config, 'AWS', 'region')

            client = get_client(access_key=access_key, secret_key=secret_key, region=region)

            latest_machine = get_latest_machine(client, state_machine_name)

            state_machine_def = open(os.path.join(path, filename), 'r').read()

            if filename.endswith(".yml") or filename.endswith(".yaml"):
                state_machine_def = json.dumps(yaml.load(state_machine_def), indent=4)
            else:
                # perform json.load on current json so the defs of previous versions can be compared reliably
                state_machine_def = json.dumps(json.load(state_machine_def), indent=4)

            if latest_machine:
                if compare_defs(latest_machine['definition'], state_machine_def):
                    print "NOP: {} code has not changed. Skipping deploy. Current version: {}".format(state_machine_name, latest_machine['name'])
                    continue

                deployed_name = get_next_version_name(latest_machine['name'])
            else:
                deployed_name = "{}-0".format(state_machine_name)

            print "  version: {}".format(deployed_name)

            role_arn = get_flattened_config_value(global_config, config, 'Machines', 'execution-role-arn')

            if not role_arn:
                print "FAIL: {} deployment failed :(".format(deployed_name)
                print "    Error! No execution role arn found. Missing execution-role-arn value in .config file?"
                print ""
                continue

            response = client.create_state_machine(
                name=deployed_name, definition=state_machine_def, roleArn=role_arn)

            deploy_info = {}

            deploy_info['name'] = deployed_name
            deploy_info['arn'] = response['stateMachineArn']
            deploy_info['date'] = str(response['creationDate'])

            deploy_file = open(os.path.join(path, state_machine_name + ".deploy"), 'w')
            deploy_file.write(json.dumps(deploy_info, indent=4))
            deploy_file.close()

            print "SUCCESS: {} deployment succeeded :D".format(deployed_name)
            print ""

def main():

    state_machine_path = sys.argv[1]

    print
    print "You just ran Esseff! Let's do this!"
    print "Version: 0.0.1"
    print "State Machine Path: {}".format(state_machine_path)
    print
    print "-=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-"

    LINTING_ENABLED = False

    print
    print "Executing Lint Step..."
    print

    try:
        subprocess.check_call(["statelint"])
        LINTING_ENABLED = True
    except:
        print "WARN: statelint command not found. No linting support :("

    if LINTING_ENABLED and not lint_state_machines(state_machine_path):
        print "One or more state machines failed linting. Exiting..."
        sys.exit(1)

    print
    print "Lint Step Complete!"
    print
    print "-=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-"
    print
    print "Executing Deploy Step..."
    print

    deploy_state_machines(state_machine_path)

    print
    print "Deploy Step Complete!"
    print
    print "-=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=--=-=-=-=-=-=-"
    print
    print "Esseff is finished. Have a nice day :D"
    print
