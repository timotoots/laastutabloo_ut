import xml.etree.ElementTree as ET
import pandas, os
from ckan.logic import action
from ckan.common import config

FILESTORAGE_PATH = config.get('ckan.storage_path') 


# Filter Dataset
def filter(context, resource):
    # Get useful metadata for the resource
    file_type = resource['format']
    file_id = resource['id']
    
    #Construct path for filestorer
    file_path = FILESTORAGE_PATH + "/resources/" + file_id[:3] + "/" +\
                file_id[3:6] + "/" + file_id[6:] 
    
    # Switch-Case for filetype differenciation
    if file_type=='XML':
        data = xml(file_path)
    elif file_type=='JSON':
        data = json(file_path)
    elif file_type=='CSV':
        data = csv(file_path)
    else:
	      print "Not a valid file type"
	  
    # Run script 
    if os.path.isfile(file_path + ".schema"):
      script = open(file_path + ".schema").read()
      data = eval(script)    

    # Complete data according to schema
    if os.path.isfile(file_path + ".script"):
      schema = open(file_path + ".script").read()
      data = complete(data, schema)
    
    # change resource
    os.remove(file_path)
    f = open(file_path, "w")
    f.write(data.to_csv(encoding='utf-8'))
    action.update.resource_update(context, {'type': 'CSV', 'format': 'CSV', 'id' : file_id})

# Change columns according to schema
def complete(data, schema):
    # Read schema
    schema = pandas.read_json(schema)
    
    for i in schema:
      if schema[i][0]=='':
        del data[i]
      elif i != schema[i][0]:
        data.rename(index=str, columns={i: schema[i][0]})
      elif i not in data:
        data[i] = schema[i][0]

    return data

# Convert XML to pandas
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

# Convert JSON to pandas
def json(file_path):
    return pandas.read_json(file_path)

# Convert CSV to pandas
def csv(file_path):
    return pandas.read_csv(file_path)
  
