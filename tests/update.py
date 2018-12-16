#!/usr/bin/env python
import urllib
import urllib2
import json
import requests
import os
import hashlib
from datetime import datetime, timedelta
from dateutil import parser


api_key = "9675909b-7627-484d-ae78-5b2932684a1b"
host = "http://127.0.0.1:5000"
hours_offset = -2
update_log_location = "/home/user/update_log"

# Writes update info to log
def log_update(id, name, time, success, details):
	f = open(update_log_location, "a")
	log = '{"id": "' + str(id) + '", "name": "' + str(name) + '", "time": "' + str(time) + '", "success": "' + str(success) + '", "details": "' + str(details) + '"}'
	f.write(log)
	f.close()
	print("Writing to log: " + str(update_log_location))

# Computes the hash of a given file
def get_hash(file_name):
	BUF_SIZE = 65536
	md5 = hashlib.md5()
	with open(file_name, "rb") as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			md5.update(data)
	return md5

# Gets current package list with resources from the CKAN server
def get_resources(host, api_key):
	resp = requests.post(host + "/api/action/current_package_list_with_resources",
		headers={"X-CKAN-API-Key": api_key})
	return resp

# Updates a resource using the given resource metadata (given as a dict)
def update_resource_metadata(host, api_key, resource):
	resp = requests.post(host + "/api/action/resource_update",
		data=resource,
		headers={"X-CKAN-API-Key": api_key})
	return resp

# Gets hash of a file and compares it to a given hash
def compare_file_to_hash(file_name, hash):
	return get_hash(file_name).hexdigest() == hash

# Compares the hashes of two files
def compare_files(file1, file2):
	return get_hash(file1).hexdigest() == get_hash(file2).hexdigest()

# Used to manually update last_modified value in resource metadata
# Note: CKAN acts weird when handling last_modified in resource.update
# Currently not used, but might become necessary
def update_last_modified(host, api_key, resource_id, hours_offset):
	# Get resource metadata
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	# Update hash value
	resource = json.loads(resp.content)["result"]
	current_time = datetime.now() + timedelta(hours=hours_offset)
	resource["last_modified"] = current_time
	resp = update_resource_metadata(host, api_key, resource)
	return resp

# Used to add/update resource hash when updating resource
def update_hash(host, api_key, resource_id, new_hash):
	# Get resource metadata
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	# Update hash value
	resource = json.loads(resp.content)["result"]
	resource["hash"] = new_hash
	# Update resource metadata on CKAN
	resp = update_resource_metadata(host, api_key, resource)
	return resp

# Used to add URL from which to update to resource metadata
def update_source_url(host, api_key, resource_id):
	# Get resource metadata
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	resource = json.loads(resp.content)["result"]
	# Update source_url value
	resource["source_url"] = resource["url"]
	# Update resource metadata on CKAN
	resp = update_resource_metadata(host, api_key, resource)
	return resp

# Gets file from filestore, compares hashes. If no filestore, update either way
# Returns True if hashes match (-> no update needed)
def handle_missing_hash(host, api_key, resource_id, source_file):
	# Get resource metadata
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	resource = json.loads(resp.content)["result"]
	# Check if resource in filestore. If true, return source_url
	url = resource["url"]
	if url[0:len(host)] == host:
		print("Getting hash from filestore")
		# Download file from filestore, calculate hash
		res = download_file(resource_source_url, "server_file", resource)
		if res:
			server_file = open("server_file")
			res = compare_files(server_file, source_file)
			os.remove("server_file")
			return res
		else:
			print("Failed download from server")
			return False

# Method for getting URL from which to update from
# Returns URL if all ok, False if resource can't be updated
def handle_url(host, api_key, resource_id):
	# Get resource metadata
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	resource = json.loads(resp.content)["result"]
	url = resource["url"]

	# Check if resource has "source_url" field. If not, use empty string
	if "source_url" in resource.keys():
		source_url = resource["source_url"]
	else:
		print("Resource missing source_url field, adding empty field")
		resource["source_url"] = ""
		source_url = ""
		resp = update_resource_metadata(host, api_key, resource)

	# Check if resource in filestore
	if url[0:len(host)] == host:
		# Check if source_url is ok
		if source_url[0:len(host)] == host or not source_url:
			print("Resource only in filestore, can't update")
			log_update(resource["id"], resource["name"], datetime.now() + timedelta(hours=hours_offset), "Fail", "File only in filestore, no source url")
			return False
		else:
			return source_url
	# Resource not in filestore. Set source_url = url, return url
	else:
		resource["source_url"] = resource["url"]
		resp = update_resource_metadata(host, api_key, resource)
		return resource["url"]

# Main def, handles entire update process.
def handle_update_resource(host, api_key, resource_id):
	# If update interval exceeded, download files and check if newer version available.
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	resource = json.loads(resp.content)["result"]
	try:
		# Get url for updating
		resource_source_url = handle_url(host, api_key, resource["id"])
		
		# If resource_source_url != False, get file name from url. If not, name = resource name + type
		if resource_source_url:
			file_name = str(resource_source_url).split("/")[len(str(resource_source_url).split("/"))-1]
		else:
			file_name = resource["name"] + resource["type"]
		
		# True if resource_source_url is not broken 
		res = download_file(resource_source_url, file_name, resource)

		if res:
			source_file = open(file_name)
			# Get hash from resource metadata.
			# If None, check if resource in filestore, if yes then get hash of that file
			resource_hash = resource["hash"]
			if not resource_hash:
				if not handle_missing_hash(host, api_key, resource["id"], source_file):
					resp = update_resource(host, api_key, resource["id"], file_name)
					print("Update successful with missing hash? " + str(json.loads(resp.content)["success"]))
					log_update(resource["id"], resource["name"], datetime.now() + timedelta(hours=hours_offset), "Success", "Success with missing hash")
			else:
				comp = compare_file_to_hash(file_name, resource_hash)
				if not comp:
					resp = update_resource(host, api_key, resource["id"], file_name)
					print("Update successful? " + str(json.loads(resp.content)["success"]))
					log_update(resource["id"], resource["name"], datetime.now() + timedelta(hours=hours_offset), "Success", "")
				else:
					print("Hashes match - already latest version, not updating")
			os.remove(file_name)
	except KeyError as e:
		print(e)
		return False

# Uploads new_file to package
def update_resource(host, api_key, resource_id, new_file):
	# Update file on CKAN filestore
	f = open(new_file)
	# Get resource metadata
	resp = requests.post(host + "/api/action/resource_show",
		data={"id": resource_id},
		headers={"X-CKAN-API-Key": api_key})
	resource = json.loads(resp.content)["result"]
	resp = requests.post(host + "/api/action/resource_update",
		data=resource,
		headers={"X-CKAN-API-Key": api_key},
		files=[("upload", f)])
	f.close()
	success = json.loads(resp.content)["success"]
	print("File upload successful? " + str(success))
	if not success:
		return resp
	else:
		# Update resource hash
		new_hash = get_hash(new_file).hexdigest()
		update_hash(host, api_key, resource_id, new_hash)
		return resp

# Tries to download file from link, saves to %CWD%/file_name
# Returns True if link ok, False if link broken
def download_file(link, file_name, resource):
	try:
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
		return True
	except urllib2.URLError as e:
		print(e)
		log_update(resource["id"], resource["name"], datetime.now() + timedelta(hours=hours_offset), "Fail", e)
		return False

	except urllib2.HTTPError as e:
		print(e)
		log_update(resource["id"], resource["name"], datetime.now() + timedelta(hours=hours_offset), "Fail", e)
		return False


# Checks all resources, updates files if able and needed.
# hours_offset should be set different than 0 if there's a difference in server time vs local time
# For example, if server is 2 hours behind, set hours_offset to -2
def check_for_update(host, api_key, hours_offset):
	# Get all datasets, resources
	resp = get_resources(host, api_key)
	resp_json = json.loads(resp.content)["result"]
	
	for dataset in resp_json:
		name = dataset["name"]
		resources = dataset["resources"]
		print("\n\n" + "--------------------------------------------------------------")
		print("Dataset: " + name)
		print("--------------------------------------------------------------")
		for resource in resources:
			# Check the 'last_modified' value. If None, use 'created' instead.
			last_mod = resource["last_modified"]
			if last_mod == None:
				last_mod = resource["created"]
			last_mod = parser.parse(str(last_mod))

			# Check the 'update_interval' value. If None, do not update
			if "update_interval" in resource.keys():
				update_interval = resource["update_interval"]
			else:
				update_interval = False
			print("\nResource: " + resource["name"])
			print("Last modified: " + str(last_mod))
			print("Update interval: " + str(update_interval))
			
			# Check if its time to update.
			update = False
			if update_interval == "5min":
				update = (datetime.now() + timedelta(hours=hours_offset)) >= (last_mod + timedelta(minutes=5))
			elif update_interval == "hourly":
				update = (datetime.now() + timedelta(hours=hours_offset)) >= (last_mod + timedelta(hours=1))
			elif update_interval == "daily":
				update = (datetime.now() + timedelta(hours=hours_offset)) >= (last_mod + timedelta(days=1))
			elif update_interval == "weekly":
				update = (datetime.now() + timedelta(hours=hours_offset)) >= (last_mod + timedelta(days=7))
			elif update_interval == "monthly":
				update = (datetime.now() + timedelta(hours=hours_offset)) >= (last_mod + timedelta(days=30))
			elif update_interval == "annually":
				update = (datetime.now() + timedelta(hours=hours_offset)) >= (last_mod + timedelta(days=365))

			print("Should we update? " + str(update))
			if update:
				handle_update_resource(host, api_key, resource["id"])
			 

# --------------------------------------------------------------------------------------------------
# Run updater
# --------------------------------------------------------------------------------------------------

check_for_update(host, api_key, hours_offset)
		

