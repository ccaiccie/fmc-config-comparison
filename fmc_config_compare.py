#!/usr/bin/env python3
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
Then it compares these actual configurations to previously saved gold configuration.
If any of the objects have changed, it saves the changes in report.csv file.
"""

# Import libraries
import sys,os
import csv
import json
from pprint import pprint
#import needed library for diff (https://pypi.python.org/pypi/json-delta/)
import json_delta
import connect

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

# Create files to store actual configuration
policylist = open("policyList_actual.json", "w")
networklist = open("networkList_actual.json", "w")
grouplist = open("groupList_actual.json", "w")

# Initiate dictionaries to populate with data
policies = {}
networks = {}
groups = {}


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
json.dump(networks,networklist,indent=4, separators=(',', ': '))
networklist.close()

# Write all the network groups to one file for tracking
json.dump(groups,grouplist,indent=4, separators=(',', ': '))
grouplist.close()

# Open GOLD configuration files and Actual configuration files that was just saved from the server

policy_goldfile = open("policyList_gold.json",'r')
policy_actualfile = open("policyList_actual.json",'r')

net_goldfile = open("networkList_gold.json",'r')
net_actualfile = open("networkList_actual.json",'r')

groups_goldfile = open("groupList_gold.json",'r')
groups_actualfile = open("groupList_actual.json",'r')

policy_goldconfig = json.loads(policy_goldfile.read())
policy_actualconfig = json.loads(policy_actualfile.read())

net_goldconfig = json.loads(net_goldfile.read())
net_actualconfig = json.loads(net_actualfile.read())

groups_goldconfig = json.loads(groups_goldfile.read())
groups_actualconfig = json.loads(groups_actualfile.read())

# Create CSV file for reporting
headers = ["Object Name","Object Type","Status","Index","Link","JSON Path","Expected Value","Actual Value"]
report_csv = csv.writer(open("report.csv","w"),delimiter = ",", quoting = csv.QUOTE_ALL)
report_csv.writerow(headers)

print("********************* Access Control Policy Comparison *************************")
# Iterate of all policies to compair with GOLD configuration
if policy_goldconfig == policy_actualconfig:
	print("Existing AC policy configuration is identical to GOLD config")
else:
	print("Existing AC policy configuration is NOT identical to GOLD config. Please check report.")
	
	# Check if the policies from gold config exist is actual config
	for key in policy_goldconfig:
		if key not in policy_actualconfig:
			print('Expected policy {0} missing from actual config'.format(key))

			# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
			if "items" not in policy_goldconfig[key]:
				report_data = [key,"AC Policy","AC Policy is missing from actual config","N/A","N/A","","",""]
				report_csv.writerow(report_data)
			else:
				report_data = [key,"AC Policy","AC Policy is missing from actual config",policy_goldconfig[key]["items"][0]["metadata"]['accessPolicy']['id'],policy_goldconfig[key]["links"]["self"],"","",""]
				report_csv.writerow(report_data)
		else:
			if policy_goldconfig[key] == policy_actualconfig[key]:
				print('Policy {0} configuration is identical to GOLD config'.format(key))

				# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
				if "items" not in policy_goldconfig[key]: # Check if policy is incomplete
					report_data = [key,"AC Policy","AC Policy is identical to GOLD config","N/A","N/A","","",""]
					report_csv.writerow(report_data)
				else:
					report_data = [key,"AC Policy","AC Policy is identical to GOLD config",policy_goldconfig[key]["items"][0]["metadata"]['accessPolicy']['id'],policy_goldconfig[key]["links"]["self"],"","",""]
					report_csv.writerow(report_data)
			else:
				print('Policy {0} configuration is NOT identical to GOLD config'.format(key))
				expected = json_delta.diff(policy_actualconfig[key],policy_goldconfig[key],verbose=False)
				diff = json_delta.diff(policy_goldconfig[key],policy_actualconfig[key],verbose=False)
				for index in range(len(diff)): #iterate through all mismatches found by json_delta.diff function
					if len(diff[index]) == 1:
						diff[index].append('None')
					if len(expected[index]) == 1:
						expected[index].append('None')
					print('		JSON Object path: ',diff[index][0])
					print('		Expected value: {0} \n		Actual value: {1}\n'.format(expected[index][1],diff[index][1]))
					
					# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
					if "items" not in policy_goldconfig[key]: # Check if policy is incomplete					
						report_data = [key,"AC Policy","Policy configuration is NOT identical to GOLD config","N/A","N/A",diff[index][0],expected[index][1],diff[index][1]]
						report_csv.writerow(report_data)
					else:
						report_data = [key,"AC Policy","Policy configuration is NOT identical to GOLD config",policy_goldconfig[key]["items"][0]["metadata"]['accessPolicy']['id'],policy_goldconfig[key]["links"]["self"],diff[index][0],expected[index][1],diff[index][1]]
						report_csv.writerow(report_data)


	# Check if the policies from actual config exist is gold config to determine new policies
	for key in policy_actualconfig:
		if key not in policy_goldconfig:			
			print('New policy {0} in actual config that is not present in GOLD config'.format(key))
			# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
			if "items" not in policy_actualconfig[key]: # Check if policy is incomplete
				report_data = [key,"AC Policy","New AC Policy in actual config that is not present in GOLD config","N/A","N/A","","",""]
				report_csv.writerow(report_data)
			else:
				report_data = [key,"AC Policy","New AC Policy in actual config that is not present in GOLD config",policy_actualconfig[key]["items"][0]["metadata"]['accessPolicy']["id"],policy_actualconfig[key]["links"]["self"],"","",""]
				report_csv.writerow(report_data)


# Iterate of all network and host objects to compair with GOLD configuration
print("********************* Network and Hosts Objects Comparison *************************")
if net_goldconfig == net_actualconfig :
	print("Existing network objects configuration is identical to GOLD config")
else:
	print("Existing network objects configuration is NOT identical to GOLD config. Please check report.")
	# Check if network objects from gold config exist is actual config
	for net in net_goldconfig:
		if net not in net_actualconfig:
			print('Expected {0} object {1} missing from actual config'.format(net_goldconfig[net]["type"],net))
			# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
			report_data = [net,net_goldconfig[net]["type"],"Object is missing from actual config",net_goldconfig[net]["id"],net_goldconfig[net]["links"]["self"],"","",""]
			report_csv.writerow(report_data)

		else:
			if net_goldconfig[net] == net_actualconfig[net]:
				print('{0} object {1} configuration is identical to GOLD config'.format(net_goldconfig[net]["type"],net))
				# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
				report_data = [net,net_goldconfig[net]["type"],"Object configuration is identical to GOLD config",net_goldconfig[net]["id"],net_goldconfig[net]["links"]["self"],"","",""]
				report_csv.writerow(report_data)

			else:
				print('{0} object {1} configuration is NOT identical to GOLD config'.format(net_goldconfig[net]["type"],net))
				expected = json_delta.diff(net_actualconfig[net],net_goldconfig[net],verbose=False)
				diff = json_delta.diff(net_goldconfig[net],net_actualconfig[net],verbose=False)
				for index in range(len(diff)): # Iterate through all mismatches found by json_delta.diff function
					if len(diff[index]) == 1:
						diff[index].append('None')
					if len(expected[index]) == 1:
						expected[index].append('None')
					print('		JSON Object path: ',diff[index][0])
					print('		Expected value: {0} \n		Actual value: {1}\n'.format(expected[index][1],diff[index][1]))
					# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
					report_data = [net,net_goldconfig[net]["type"],"Object configuration is NOT identical to GOLD config",net_goldconfig[net]["id"],net_goldconfig[net]["links"]["self"],diff[index][0],expected[index][1],diff[index][1]]
					report_csv.writerow(report_data)

	# Check if the policies from actual config exist is gold config to determine new policies
	for net in net_actualconfig:
		if net not in net_goldconfig:		
			print('New {0} object {1} in actual config that is not present in GOLD config'.format(net_actualconfig[net]["type"],net))
			# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
			report_data = [net,net_actualconfig[net]["type"],"New Network or Host object in actual config that is not present in GOLD config",net_actualconfig[net]["id"],net_actualconfig[net]["links"]["self"],"","None",net_actualconfig[net]]
			report_csv.writerow(report_data)

# Iterate of all network groups to compair with GOLD configuration
print("********************* Network Groups Comparison *************************")
if groups_goldconfig == groups_actualconfig :
	print("Existing network groups configuration is identical to GOLD config")
else:
	print("Existing network groups configuration is NOT identical to GOLD config. Please see report.")
	# Check if network objects from gold config exist is actual config
	for group in groups_goldconfig:
		if group not in groups_actualconfig:
			print('Expected group {0} missing from actual config'.format(group))
			# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
			report_data = [group,groups_goldconfig[group]["type"],"Group is missing from actual config",groups_goldconfig[group]["id"],groups_goldconfig[group]["links"]["self"],"","",""]
			report_csv.writerow(report_data)
		else:
			if groups_goldconfig[group] == groups_actualconfig[group]:
				print('Group {0} configuration is identical to GOLD config'.format(group))
				#  Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
				report_data = [group,groups_goldconfig[group]["type"],"Group configuration is identical to GOLD config",groups_goldconfig[group]["id"],groups_goldconfig[group]["links"]["self"],"","",""]
				report_csv.writerow(report_data)

			else:
				print('Group {0} configuration is NOT identical to GOLD config'.format(group))
				expected = json_delta.diff(groups_actualconfig[group],groups_goldconfig[group],verbose=False)
				diff = json_delta.diff(groups_goldconfig[group],groups_actualconfig[group],verbose=False)
				for index in range(len(diff)): # Iterate through all mismatches found by json_delta.diff function
					if len(diff[index]) == 1:
						diff[index].append('None')
					if len(expected[index]) == 1:
						expected[index].append('None')
					print('		JSON Object path: ',diff[index][0])
					print('		Expected value: {0} \n		Actual value: {1}\n'.format(expected[index][1],diff[index][1]))
					# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
					report_data = [group,groups_goldconfig[group]["type"],"Group configuration is NOT identical to GOLD config",groups_goldconfig[group]["id"],groups_goldconfig[group]["links"]["self"],diff[index][0],expected[index][1],diff[index][1]]
					report_csv.writerow(report_data)


	# Check if the policies from actual config exist is gold config to determine new policies
	for group in groups_actualconfig:
		if group not in groups_goldconfig:		
			print('New group {0} in actual config that is not present in GOLD config'.format(group))
			# Build report ["Object Name","Object Type","Status","Id","Link","JSON Path","Expected Value","Actual Value"]
			report_data = [group,groups_actualconfig[group]["type"],"New group in actual config that is not present in GOLD config",groups_actualconfig[group]["id"],groups_actualconfig[group]["links"]["self"],"","None",groups_actualconfig[group]]
			report_csv.writerow(report_data)


#Close all configuration files

policy_goldfile.close()
policy_actualfile.close()

net_goldfile.close()
net_actualfile.close()

groups_goldfile.close()
groups_actualfile.close()