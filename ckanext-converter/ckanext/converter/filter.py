import xml.etree.ElementTree as ET
import pandas, os
import ckan.logic.action as act

from ckan.common import config
FILESTORAGE_PATH = config.get('ckan.storage_path') 

def filter(context, resource):
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
    if os.path.isfile(file_path + ".schema"):
      script = open(file_path + ".schema").read()
      data = eval(script)    

    # ----------------------------------------
    # Complete
    # ----------------------------------------
    if os.path.isfile(file_path + ".script"):
      schema = open(file_path + ".script").read()
      data = complete(data, schema)
    
    # change resource
    os.remove(file_path)
    f = open(file_path, "w")
    f.write(data.to_csv())
    act.update.resource_update(context, {'format': 'CSV', 'id' : file_id})


def complete(data, schema):
    # Read schema
    schema = json(schema)
    
    # Remove columns
    # Add columns
    # Change column names
    # Change column type 

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
  
