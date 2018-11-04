import ujson, csv

def filter(resource):
    datatype = get_data_types(resource)
    if datatype=='XML':
        xml_to_csv(resource)
    elif datatype=='JSON':
        json_to_csv(resource)
    elif datatype=='CSV':
        print resource['upload']
    else:
	print "error"

def get_data_types(resource):
    return resource['type']

def json_to_csv(json):
    print resource['upload']

def xml_to_csv(xml):
    print resource['upload']


