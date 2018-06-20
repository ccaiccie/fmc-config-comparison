#!/bin/env python3
"""
NOTE: this is a Proof of Concept script, please test before using in production!

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

This script pulls Access Control Policies, Host and Networs Objects and Network Group Objects from FMC.
Then it compares these actual configurations to previously saved gold configulation.
If any of the objects have changed, it saves the changes in report.csv file.
"""

# Import libraries
import connect
import sys,os
import json
import pprint

# Input FMC url, username and password
host = "fmcurl"    # INPUT REQUIRED
if len(sys.argv) > 1:
    host = sys.argv[1]
username = "username"    # INPUT REQUIRED
if len(sys.argv) > 2:
    username = sys.argv[2]
password = "pwd"    # INPUT REQUIRED
if len(sys.argv) > 3:
    password = sys.argv[3]

print("Download gold configuration for AC Policies, Network and Host Object and Network Groups")
print("Connecting to the server {0}".format(host))

headers, uuid, server = connect.connect(host, username, password)

# Get the list of AC policies from the server
print("Getting the list of AC policies from the server")
data = connect.policyGET(headers, uuid, server)

# Get the list of networks and hosts from the server
print("Getting the list of networks and hosts from the server")
netdata = connect.networkGET(headers, uuid, server)

# Get the list of networks and hosts from the server
print("Getting the list of network groups from the server")
groupdata = connect.networkgroupsGET(headers, uuid, server)

# Create files to store configuration
policylist = open("policyList_gold.json", "w")
networklist = open("networkList_gold.json", "w")
grouplist = open("groupList_gold.json", "w")

policies,networks,groups = {},{},{}

# Iterate of all policies to get the detailed access rules for each policy and add them to the a structured policy 
for policy in data["items"]:
	print("Getting rules for policy: ", policy['name'])
	api_path = policy["links"]["self"] + "/accessrules?expanded=true"
	policy_rules = connect.ruleGET(headers, uuid, server, api_path)
	policies[policy["name"]] = policy_rules

# Iterate of all network and host objects to get the details and add them to the a structured list 
for network in netdata["items"]:
	networks[network["name"]] = network

# Iterate of all network groups to get the details and add them to the a structured list 
for group in groupdata["items"]:
	groups[group["name"]] = group

# Write all the policies to one file for tracking
json.dump(policies,policylist,indent=4, separators=(',', ': '))
policylist.close()

# Write all networks to one file for tracking
#json.dump(netdata["items"],networklist,indent=4, separators=(',', ': '))
json.dump(networks,networklist,indent=4, separators=(',', ': '))
networklist.close()

# Write all the network groups to one file for tracking
json.dump(groups,grouplist,indent=4, separators=(',', ': '))
grouplist.close()