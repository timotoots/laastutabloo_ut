#!/usr/bin/env python
import urllib2
import urllib
import json
import pprint
import requests
import json
import os
import hashlib
from datetime import datetime, timedelta
from dateutil import parser

api_key = "0ff60abf-e071-44a9-8f4b-7839cb302a7f"
host = "http://127.0.0.1:5000"
org_id = "testorg"

test_file = "/home/user/Downloads/liiklusjarelevalve2.csv"
test_link = "https://www.spordiregister.ee/opendata/files/spordikoolid.xml"

def get_hash(file):
	BUF_SIZE = 65536
	md5 = hashlib.md5()
	with open(file, "rb") as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			md5.update(data)
	return md5

def compare_files(file1, file2):
	return get_hash(file1).hexdigest() == get_hash(file2).hexdigest()

def compare_file_to_hash(file, hash):
	return get_hash(file).hexdigest() == hash

def download_file(link, file_name):
	url = urllib2.urlopen(link)
	f = open(file_name, 'wb')
	print("Downloading " + file_name)
	
	file_size_dl = 0
	block_sz = 8192
	
	while True:
		buffer = url.read(block_sz)
		if not buffer:
			break
		file_size_dl += len(buffer)
		f.write(buffer)
	f.close()

def upload_file(host, api_key, file_name, file_type, dataset_id, owner_org, path):
	resp = requests.post(host + "/api/action/resource_create",
		data={"name": file_name,
			"package_id": dataset_id,
			"type": file_type,
			"owner_org": owner_org},
		headers={"X-CKAN-API-Key": api_key},
		files=[("upload", file(path))])
	print(trim_response(resp.content))
	return resp

def upload_file_from_link(host, api_key, file_name, file_type, dataset_id, owner_org, link):
	# Download file
	download_file(link, file_name)
	
	# Upload file to ckan
	resp = upload_file(host, api_key, file_name, file_type, dataset_id, owner_org, file_name)

	# Delete downloaded file
	os.remove(file_name)
	
	return resp

def delete_package(host, api_key, package_id):
	resp = requests.post(host + "/api/action/resource_delete",
		data={"id": package_id},
		headers={"X-CKAN-API-Key": api_key})
	print(resp.content)
	return resp

def add_dataset(host, api_key, dataset_id):
	resp = requests.post(host + "/api/action/package_create",
		data={"name": dataset_id,
			"owner_org": "testorg"},
		headers={"X-CKAN-API-Key": api_key})
	print(trim_response(resp.content))
	return resp

def delete_dataset(host, api_key, dataset_id):
	resp = requests.post(host + "/api/action/package_delete",
		data={"id": dataset_id},
		headers={"X-CKAN-API-Key": api_key})
	print(resp.content)
	return resp

def get_package(host, api_key, package_id):
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": package_id},
		headers={"X-CKAN-API-Key": api_key})
	print(trim_response(resp.content))
	return resp

def update_package(host, api_key, package_id, new_file_path):
	resp = requests.post(host + "/api/action/resource_update",
		data={"id": package_id},
		headers={"X-CKAN-API-Key": api_key},
		files=[("upload", file(new_file_path))])
	print(trim_response(resp.content))
	return resp

def update_package_add_interval(host, api_key, resource_id, interval):
	resp = requests.post(host + "/api/action/resource_update",
		data={"id": resource_id, "update_interval": interval},
		headers={"X-CKAN-API-Key": api_key})
	#print(trim_response(resp.content))
	return resp

def trim_response(content):
	result = json.loads(content)["result"]
	remove = ["cache_last_updated", "datastore_active", "hash", "description", "type", "mimetype_inner", "mimetype", "cache_url", "position", "resource_type", "maintainer", "relationships_as_object", "maintainer_email", "num_tags", "author", "author_email", "version", "license_id", "resources", "num_resources", "tags", "groups", "relationships_as_subject", "url", "notes", "license_title", "extras", "organization"]
	for i in remove:
		result.pop(i, None)
	return str(result)

def get_resources(host, api_key):
	resp = requests.post(host + "/api/action/current_package_list_with_resources",
		headers={"X-CKAN-API-Key": api_key})
	return resp

resp = get_resources(host, api_key)
resp_json = json.loads(resp.content)["result"]

# For adding update interval through the API
#res_id = resp_json[0]["resources"][0]["id"]
#resp = update_package_add_interval(host, api_key, res_id, "hourly")

for dataset in resp_json:
	name = dataset["name"]
	resources = dataset["resources"]
	print("\n" + "Dataset: " + name)
	for resource in resources:
		# Check the 'last_modified' value. If None, use 'created' instead.
		last_mod = resource["last_modified"]
		if last_mod == None:
			last_mod = resource["created"]
		last_mod = parser.parse(str(last_mod))

		# Check the 'update_interval' value. If not defined, do not update automatically.
		if "update_interval" in resource.keys():
			update_interval = resource["update_interval"]
		else:
			update_interval = False
		print("Resource: " + resource["name"] + ", last modified: " + str(last_mod) + ", update interval: " + str(update_interval))
		
		# Check if its time to update.
		update = False
		if update_interval == "hourly":
			update = datetime.now() >= (last_mod + timedelta(hours=1))
		elif update_interval == "daily":
			update = datetime.now() >= (last_mod + timedelta(days=1))
		elif update_interval == "weekly":
			update = datetime.now() >= (last_mod + timedelta(days=7))
		elif update_interval == "monthly":
			update = datetime.now() >= (last_mod + timedelta(days=30))
		elif update_interval == "annually":
			update = datetime.now() >= (last_mod + timedelta(days=365))

		print("Should we update? " + str(update))
		
		# If update interval exceeded, download files and check if newer version available.
		if update:
			try:
				resource_source_url = resource["source_url"]
				resource_hash = resource["hash"]
				download_file(resource_source_url, "source_file.xml")
				comp = compare_file_to_hash("source_file.xml", resource_hash)
				print("Source and server files hashes match? " + str(comp))
				if not comp:
					resp = update_package(host, api_key, resource["id"], "source_file.xml")
					print("Update successful? " + str(json.loads(resp.content)["success"]))
				os.remove("source_file.xml")
			except KeyError:
				print("error getting resource hash or source URL") 
		
		
		
		



