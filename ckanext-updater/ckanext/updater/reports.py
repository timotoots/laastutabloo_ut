'''
Working examples - simple tag report.
'''

from ckan import model
from ckan.common import OrderedDict
from ckanext.report import lib

import json

update_log_location = '/home/user/update_log'

def update_report():
	with open(update_log_location) as f:
    		content = f.readlines()
	full_history = []
	grouped_history = []
	failed_history = []

	group_dict = {}
	names = {}
	
	for line in content:
		json_line = json.loads(line)
		id = json_line["id"]
		name = json_line["name"]
		time = json_line["time"]
		success = json_line["success"]
		details = json_line["details"]
		
		table_line = OrderedDict((
			("id", id),
			("name", name),
			("time", time),
			("success", success),
			("details", details)))

		group_line = OrderedDict((
			("time", time),
			("success", success),
			("details", details)))

		if id in group_dict.keys():
			group_dict[id].append(group_line)
		else:
			group_dict[id] = [group_line]
		names[id] = name

		full_history.append(table_line)
		if success == "Fail":
			failed_history.append(table_line)
	
	for id in group_dict.keys():
		if len(group_dict[id]) > 10:
			group_dict[id] = group_dict[id][len(group_dict[id]) - 11: len(group_dict[id]) - 1]
		grouped_history.append(OrderedDict((
			("id", id),
			("name", names[id]),
			("history", group_dict[id]))))
	
	return {'table': list(reversed(full_history)),
		'fail_table': failed_history,
		'grouped_table': grouped_history}
	
update_report_info = {
    'name': 'update-report',
    'description': 'Report of resource updates',
    'option_defaults': OrderedDict([]),
    'option_combinations': None,
    'generate': update_report,
    'template': 'report/update-report.html',
    }
