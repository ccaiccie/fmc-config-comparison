"""
MODULE FOR SUPPORTING FUNCTIONS FOR FMC RESST API

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
import json
import sys
import requests
#Surpress HTTPS insecure errors for cleaner output
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Define fuction to connect to the FMC API and generate authentication token
def connect (host, username, password):
	headers = {'Content-Type': 'application/json'}
	path = "/api/fmc_platform/v1/auth/generatetoken"
	server = "https://"+host 
	url = server + path
	try:
		r = requests.post(url, headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify=False)
		auth_headers = r.headers
		token = auth_headers.get('X-auth-access-token', default=None)
		uuid = auth_headers.get('DOMAIN_UUID', default=None)
		if token == None:
			print("No Token found, I'll be back terminating....")
			sys.exit()
	except Exception as err:
		print ("Error in generating token --> "+ str(err))
		sys.exit()
	headers['X-auth-access-token'] = token

	return headers,uuid,server

def policyGET (headers, uuid, server):
	api_path= "/api/fmc_config/v1/domain/" + uuid + "/policy/accesspolicies"
	url = server+api_path
	try:
		r = requests.get(url, headers=headers, verify=False)
		status_code = r.status_code
		resp = r.text
		json_response = json.loads(resp)
		print("status code is: "+ str(status_code))
		if status_code == 200:
			print("GET was sucessfull...")
		else:
			r.raise_for_status()
			print("error occured in GET -->"+resp)
	except requests.exceptions.HTTPError as err:
		print ("Error in connection --> "+str(err))
	finally:
		if r: r.close()
	return json_response

def ruleGET(headers, uuid, server, url):
	try:
		r = requests.get(url, headers=headers, verify=False)
		status_code = r.status_code
		resp = r.text
		json_response = json.loads(resp)
		print("status code is: "+ str(status_code))
		if status_code == 200:
			print("GET was sucessfull...")
		else:
			r.raise_for_status()
			print("error occured in GET -->"+resp)
	except requests.exceptions.HTTPError as err:
		print ("Error in connection --> "+str(err))
	finally:
		if r: r.close()
	return json_response

def apiGET(headers, uuid, server, api_path):
	try:
		url = server+api_path
		r = requests.get(url, headers=headers, verify=False)
		status_code = r.status_code
		resp = r.text
		json_response = json.loads(resp)
		print("status code is: "+ str(status_code))
		if status_code == 200:
			print("GET was sucessfull...")
		else:
			r.raise_for_status()
			print("error occured in GET -->"+resp)
	except requests.exceptions.HTTPError as err:
		print ("Error in connection --> "+str(err))
	finally:
		if r: r.close()
	return json_response
	
def networkGET (headers, uuid, server):
	api_path= "/api/fmc_config/v1/domain/" + uuid + "/object/networkaddresses?expanded=true&limit=1000"
	url = server+api_path
	try:
		r = requests.get(url, headers=headers, verify=False)
		status_code = r.status_code
		resp = r.text
		json_response = json.loads(resp)
		print("status code is: "+ str(status_code))
		if status_code == 200:
			print("GET was sucessfull...")
		else:
			r.raise_for_status()
			print("error occured in GET -->"+resp)
	except requests.exceptions.HTTPError as err:
		print ("Error in connection --> "+str(err))
	finally:
		if r: r.close()
	return json_response
	
def networkgroupsGET (headers, uuid, server):
	api_path= "/api/fmc_config/v1/domain/" + uuid + "/object/networkgroups?expanded=true&limit=1000"
	url = server+api_path
	try:
		r = requests.get(url, headers=headers, verify=False)
		status_code = r.status_code
		resp = r.text
		json_response = json.loads(resp)
		print("status code is: "+ str(status_code))
		if status_code == 200:
			print("GET was sucessfull...")
		else:
			r.raise_for_status()
			print("error occured in GET -->"+resp)
	except requests.exceptions.HTTPError as err:
		print ("Error in connection --> "+str(err))
	finally:
		if r: r.close()
	return json_response