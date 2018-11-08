#!/usr/bin/python3

import sys
import requests
import json

# 接收传入内容
msg = sys.argv[1]

config_content = open(sys.path[0] + '/cachethq_status_updater_conf.json')
config_dict = json.load(config_content)

cachethq_url = config_dict['config_main']['cachethq_url']
cachethq_api_key = config_dict['config_main']['cachethq_api_key']
cachethq_host_dict = config_dict['host']

temp_file_path = sys.path[0] + '/cachethq_status_updater.temp'


def zabbix_msg_handler():
    zbx_msg_list = msg.split('\n')
    zbx_msg_dict = dict()
    for i in zbx_msg_list:
        i_list = i.split('::')
        zbx_msg_dict[i_list[0]] = i_list[1].strip('\r')
    return zbx_msg_dict


def r_w_d_temp_file(act_type, host_name, event_id, incident_id):
    try:
        r = open(temp_file_path, 'r')
    except FileNotFoundError:
        r = open(temp_file_path, 'w')
        r.write('{}')
        r.close()
        temp_content = dict()
    else:
        temp_content = json.loads(r.read())
        r.close()

    if act_type == 'r':
        try:
            incident_id = temp_content[host_name][event_id]
        except KeyError:
            return False
        else:
            event_count = len(temp_content[host_name])
            return incident_id, event_count
    elif act_type == 'd':
        del temp_content[host_name][event_id]
        r = open(temp_file_path, 'w')
        r.write(str(json.dumps(temp_content)))
        r.close()
        return None
    elif act_type == 'w':
        if host_name in temp_content:
            temp_content[host_name][event_id] = incident_id
        else:
            id_dict = dict()
            id_dict[event_id] = incident_id
            temp_content[host_name] = id_dict
        r = open(temp_file_path, 'w')
        r.write(str(json.dumps(temp_content)))
        r.close()
        return None
    else:
        pass


def create_incidents(api_token, inc_name, inc_msg, inc_status, inc_visible, comp_id, comp_status):
    req_url = cachethq_url + 'incidents'
    payload = {
        "name": inc_name,
        "message": inc_msg,
        "status": inc_status,
        "visible": inc_visible,
        "component_id": comp_id,
        "component_status": comp_status
    }
    headers = {'X-Cachet-Token': api_token}
    req_run = requests.request('POST', req_url, data=payload, headers=headers)
    req_content = json.loads(req_run.text)
    inc_id = req_content['data']['id']
    return inc_id


def update_incidents(api_token, inc_id, inc_name, inc_msg, inc_status, inc_visible, com_id, comp_status):
    req_url = cachethq_url + 'incidents/' + str(inc_id)
    payload = {
        "name": inc_name,
        "message": inc_msg,
        "status": inc_status,
        "visible": inc_visible,
        "component_id": com_id,
        "component_status": comp_status
    }
    headers = {'X-Cachet-Token': api_token}
    req_run = requests.request('PUT', req_url, data=payload, headers=headers)
    req_content = json.loads(req_run.text)
    return req_content


def write_to_temp(temp_content):
    r = open(sys.path[0] + '/temp.temp', 'w')
    r.write(temp_content)
    r.close()


def run():
    msg_dict = zabbix_msg_handler()
    if 'start_time' in msg_dict:
        incidents_name = 'Host ' + msg_dict['host_name'] + ' has an ' + msg_dict['severity'] + ' level alarm.'
        incidents_msg = 'Event ID: ' + str(msg_dict['event_id']) + \
                        ', Event name: ' + msg_dict['event_name'] + \
                        ', Event start time: ' + msg_dict['start_time']
        if msg_dict['severity'] is 'Not classified' or 'Information':
            component_status = 2
        elif msg_dict['severity'] is 'Warning' or 'Average':
            component_status = 3
        elif msg_dict['severity'] is 'High' or 'Disaster':
            component_status = 4
        else:
            component_status = 1

        incidents_id = create_incidents(cachethq_api_key, incidents_name, incidents_msg, 2, 1,
                                        cachethq_host_dict[msg_dict['host_name']], component_status)
        r_w_d_temp_file('w', msg_dict['host_name'], msg_dict['event_id'], incidents_id)
    elif 'resolved_time' in msg_dict:
        incidents_name = 'The alarm of the ' + msg_dict['severity'] + ' level of host ' + msg_dict[
            'host_name'] + ' has been released.'
        incidents_msg = 'Event ID: ' + str(msg_dict['event_id']) + \
                        ', Event name: ' + msg_dict['event_name'] + \
                        ', Event resolved time: ' + msg_dict['resolved_time']
        incidents_id = r_w_d_temp_file('r', msg_dict['host_name'], msg_dict['event_id'], 0)[0]
        update_incidents(cachethq_api_key, incidents_id, incidents_name, incidents_msg, 4, 1,
                         cachethq_host_dict[msg_dict['host_name']], 1)
        r_w_d_temp_file('d', msg_dict['host_name'], msg_dict['event_id'], 0)
    else:
        pass


if __name__ == '__main__':
    run()
