#!/usr/bin/env python
import urllib2
import urllib
import json
import pprint
import requests
import json
import os
import hashlib

api_key = "3a3e6c64-9d9a-4ee7-99b0-fd2d26e399da"
host = "http://127.0.0.1:5000"
org_id = "testorg"

#test_file = "/home/user/Downloads/liiklusjarelevalve2.csv"
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

def trim_response(content):
	result = json.loads(content)["result"]
	remove = ["cache_last_updated", "datastore_active", "hash", "description", "type", "mimetype_inner", "mimetype", "cache_url", "position", "resource_type", "maintainer", "relationships_as_object", "maintainer_email", "num_tags", "author", "author_email", "version", "license_id", "resources", "num_resources", "tags", "groups", "relationships_as_subject", "url", "notes", "license_title", "extras", "organization"]
	for i in remove:
		result.pop(i, None)
	return str(result)

# Create a new dataset
print("Creating new dataset")
resp = add_dataset(host, api_key, "test_dataset")
print("success: " + str(json.loads(resp.content)["success"]))
raw_input()

# Get ID of created dataset
print("\nGetting ID of the created dataset")
cont = json.loads(resp.content)
dataset_id = cont["result"]["id"]
print("success: " + str(cont["success"]) + ", id: " + str(dataset_id))
raw_input()

# Upload resources
print("\nUploading new resources")
#print("From file")
#resp = upload_file(host, api_key, "uploadtest", "CSV", dataset_id, "testorg", test_file)
#print("success: " + str(json.loads(resp.content)["success"]))
#raw_input()
print("From link")
resp = upload_file_from_link(host, api_key, "linktest.xml", "XML", dataset_id, "testorg", test_link)
print("success: " + str(json.loads(resp.content)["success"]))
raw_input()

# Delete resources
print("\nDeleting packages")
resp = delete_package(host, api_key, "linktest")
print("success: " + str(json.loads(resp.content)["success"]))
resp = delete_package(host, api_key, "uploadtest")
print("success: " + str(json.loads(resp.content)["success"]))

# Delete dataset
print("\nDeleting dataset")
resp = delete_dataset(host, api_key, "test_dataset")
print("success: " + str(json.loads(resp.content)["success"]))

