import ujson, csv
import xml.etree.ElementTree as ET
import pandas

from ckan.common import config
FILESTORAGE_PATH = config.get('ckan.storage_path') 

def filter(resource, schema, script):
    # Get useful metadata for the resource
    file_type = resource['type']
    file_id = resource['id']
    
    #Construct path for filestorer
    file_path = FILESTORAGE_PATH + "/resources/" + file_id[:3] + "/" +\
                file_id[3:6] + "/" + file_id[6:]
        

    # ----------------------------------------
    # Convert()
    # ----------------------------------------

    # Switch-Case for filetype differenciation
    if file_type=='XML':
        data = xml(file_path)
    elif file_type=='JSON':
        data = json(file_path)
    elif file_type=='CSV':
        data = csv(file_path)
    else:
	      print "Not a valid file type"
	  
    # ----------------------------------------
    # Run script
    # ----------------------------------------  
        
    # data = script(data, schema, script)    

    # ----------------------------------------
    # Complete
    # ----------------------------------------
    
    #data = complete(data, schema, script)
    
    # Upload resource
    print data.to_csv()
    
       


def complete(data, schema):
    # Read schema
    # Convert CSV to pandas
    # Remove columns
    # Add columns
    # Change column names
    # Change column type 
    # Export Pandas to CSV

    return data


def xml(file_path):
    tree = ET.parse(file_path)

    data = []
    tmp = {}
    for i in tree.iterfind('./*'):
        for j in i.iterfind('*'):
            tmp[j.tag] = j.text
        data.append(tmp)
        tmp = {}

    return pandas.DataFrame(data)

def json(file_path):
    return pandas.read_json(file_path)

def csv(file_path):
    return pandas.read_csv(file_path)
  
