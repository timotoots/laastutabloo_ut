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
    
    # Validate()
    # ----------------------------------------
    
    # Switch-Case for filetype differenciation
    if file_type=='XML':
        return xml_to_csv(file_id, file_path)
    elif file_type=='JSON':
        return json_to_csv(file_id, file_path)
    elif file_type=='CSV':
        return file_path
    else:
	print "error"
	        
    # ----------------------------------------
    # Convert()
    # ----------------------------------------
    # Complete()
    # ----------------------------------------
    # Validate()
    # ----------------------------------------
    


# Convert JSON to CSV
def json_to_csv(file_id, file_path):
    return file_path

# Convert XML to CSV
def xml_to_csv(file_id, file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    Resident_data = open(FILESTORAGE_PATH + "/converted/" + file_id, 'w')
    csvwriter = csv.writer(Resident_data)
    for i in root:
        row = []
        for j in i:
            if j.text: 
                row.append(j.text.encode('utf-8'))
        csvwriter.writerow(row)
    return FILESTORAGE_PATH + "/converted/" + file_id

