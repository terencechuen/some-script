import sys

import json
import requests
from datetime import datetime, timedelta

try:
    config_content = open(sys.path[0] + '/config.json')
except Exception as e:
    print(e)
    sys.exit(0)
else:
    config_dict = json.load(config_content)

cachethq_url = config_dict['config_main']['cachethq_url']
cachethq_api_key = config_dict['config_main']['cachethq_api_key']


def get_datetime():
    datetime_now = datetime.today().strftime("%Y-%m-%d %H:%M:00")
    datetime_now = datetime.strptime(datetime_now, '%Y-%m-%d %H:%M:%S')
    datetime_old = datetime_now - timedelta(minutes=3)

    timestamp_now = datetime_now.timestamp()
    timestamp_now = int(timestamp_now * 1000)

    timestamp_old = datetime_old.timestamp()
    timestamp_old = int(timestamp_old * 1000)

    output_dict = dict()
    output_dict['timestamp_now'] = str(timestamp_now)
    output_dict['timestamp_old'] = str(timestamp_old)
    return output_dict


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


def get_number_of_visits(es_url, es_index_name, es_gte, es_lte):
    payload = {
        "size": 0,
        "_source": {
            "excludes": []
        },
        "aggs": {},
        "stored_fields": [
            "@timestamp"
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "match_all": {}
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": es_gte,
                                "lte": es_lte,
                                "format": "epoch_millis"
                            }
                        }
                    }
                ]
            }
        }
    }
    headers = {'content-type': 'application/json'}
    req_run = requests.post(es_url + es_index_name + '/_search', data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    req_value = req_content['hits']['total']
    return str(req_value)


def cachethq_metrics_add_point(api_token, metric_id, metric_value, metric_timestamp):
    req_url = cachethq_url + 'metrics/' + str(metric_id) + '/points'
    if metric_timestamp is None:
        payload = {
            "value": metric_value
        }
    else:
        payload = {
            "value": metric_value,
            "timestamp": metric_timestamp
        }
    headers = {'X-Cachet-Token': api_token}
    req_run = requests.request('POST', req_url, data=payload, headers=headers)
    req_content = json.loads(req_run.text)
    print(req_content)
    return req_content


def run_es6(config_json, time_now, time_old):
    es6_api_url = config_json['es6_api_url']
    es6_index = config_json['es6_index']
    metric_id = config_json['metric_id']

    item_value = get_number_of_visits(es6_api_url, es6_index, time_old, time_now)
    cachethq_metrics_add_point(cachethq_api_key, metric_id, item_value, time_now[0:10])


def run():
    timestamp_dict = get_datetime()
    timestamp_now = timestamp_dict['timestamp_now']
    timestamp_old = timestamp_dict['timestamp_old']

    for i in config_dict['config']:
        if i['services'] == 'zbx':
            run_zbx(i, timestamp_now)
        elif i['services'] == 'es6':
            run_es6(i, timestamp_old, timestamp_now)


if __name__ == "__main__":
    run()
