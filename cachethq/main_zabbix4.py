import json
import requests
import uuid


def zbx_login(zbx_url, zbx_usrname, zbx_pawd):
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": zbx_usrname,
            "password": zbx_pawd
        },
        "id": 1,
    }
    headers = {'content-type': 'application/json'}
    req_run = requests.post(zbx_url, data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    return req_content


def zbx_logout(zbx_url, zbx_login_id, zbx_login_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "user.logout",
        "params": [],
        "id": zbx_login_id,
        "auth": zbx_login_token
    }
    headers = {'content-type': 'application/json'}
    req_run = requests.post(zbx_url, data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    return req_content


def get_zbx_item_value(zbx_url, zbx_token, zbx_item_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": 0,
            "itemids": zbx_item_id,
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 1
        },
        "auth": zbx_token,
        "id": 1
    }
    headers = {'content-type': 'application/json'}
    req_run = requests.post(zbx_url, data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    req_value = req_content['result'][0]['value']
    return str(req_value)


def run_zbx(config_json, time_now):
    zbx_api_url = config_json['zbx_api_url']
    zbx_username = config_json['zbx_username']
    zbx_passwd = config_json['zbx_passwd']
    zbx_item_id = config_json['zbx_item_id']
    metric_id = config_json['metric_id']

    login_content = zbx_login(zbx_api_url, zbx_username, zbx_passwd)
    zbx_token = login_content['result']
    item_value = get_zbx_item_value(zbx_api_url, zbx_token, zbx_item_id)
    zbx_logout(zbx_api_url, login_content['id'], zbx_token)
    cachethq_metrics_add_point(cachethq_api_key, metric_id, item_value, time_now[0:10])
