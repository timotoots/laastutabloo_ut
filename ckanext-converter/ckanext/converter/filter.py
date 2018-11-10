import ujson, csv
import xml.etree.ElementTree as ET

from ckan.common import config
FILESTORAGE_PATH = config.get('ckan.storage_path') 

def filter(resource):
    # Get useful metadata for the resource
    file_type = resource['type']
    file_id = resource['id']
    
    #Construct path for filestorer
    file_path = FILESTORAGE_PATH + "/resources/" + file_id[:3] + "/" +\
                file_id[3:6] + "/" + file_id[6:]
    
    # Switch-Case for filetype differenciation
    if file_type=='XML':
        return xml_to_csv(file_path)
    elif file_type=='JSON':
        return json_to_csv(file_path)
    elif file_type=='CSV':
        return file_path
    else:
	    print "error"

# Convert JSON to CSV
def json_to_csv(json):
    return json

# Convert XML to CSV
def xml_to_csv(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    Resident_data = open('/tmp/ResidentData.csv', 'w')
    csvwriter = csv.writer(Resident_data)
    for i in root:
        for j in i:
            j=j.text
        csvwriter.writerow(i)
    return open('/tmp/ResidentData.csv', 'r').read(100)

