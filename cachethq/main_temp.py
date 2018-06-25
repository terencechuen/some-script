import json
from datetime import datetime, timedelta

import requests

zbx_api_url = 'http://zabbix.t.com/api_jsonrpc.php'
es6_api_url = 'http://es6-node1.t.com:9200/'
cachethq_url = 'https://status.ngx.hk/api/v1/'


def get_datetime():
    datetime_now = datetime.today().strftime("%Y-%m-%d %H:%M:00")
    datetime_now = datetime.strptime(datetime_now, '%Y-%m-%d %H:%M:%S')
    datetime_old = datetime_now - timedelta(minutes=1)

    timestamp_now = datetime_now.timestamp()
    timestamp_now = int(timestamp_now * 1000)

    timestamp_old = datetime_old.timestamp()
    timestamp_old = int(timestamp_old * 1000)

    output_dict = dict()
    output_dict['timestamp_now'] = str(timestamp_now)
    output_dict['timestamp_old'] = str(timestamp_old)
    return output_dict


def zbx_login(zbx_username, zbx_passwd, zbx_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": zbx_username,
            "password": zbx_passwd
        },
        "id": zbx_id,
    }
    headers = {'content-type': 'application/json'}
    req_run = requests.post(zbx_api_url, data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    return req_content


def zbx_logout(zbx_login_id, zbx_login_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "user.logout",
        "params": [],
        "id": zbx_login_id,
        "auth": zbx_login_token
    }
    headers = {'content-type': 'application/json'}
    req_run = requests.post(zbx_api_url, data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    return req_content


def get_zbx_item_value(zbx_token, zbx_item_id):
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
    req_run = requests.post(zbx_api_url, data=json.dumps(payload), headers=headers)
    req_content = json.loads(req_run.text)
    req_value = req_content['result'][0]['value']
    return str(req_value)


def get_number_of_visits(es_index_name, es_gte, es_lte):
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
    req_run = requests.post(es6_api_url + es_index_name + '/_search', data=json.dumps(payload), headers=headers)
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
    return req_content


def run_main():
    timestamp_dict = get_datetime()
    timestamp_now = timestamp_dict['timestamp_now']
    timestamp_old = timestamp_dict['timestamp_old']

    login_content = zbx_login('admin', 'zabbix', timestamp_now)
    zbx_token = login_content['result']
    item_value = get_zbx_item_value(zbx_token, 31712)
    zbx_logout(login_content['id'], zbx_token)
    cachethq_metrics_add_point('Cachet_token', 1, item_value, timestamp_now[0:10])

    item_value = get_number_of_visits('public-ngx-alias', timestamp_old,
                                      timestamp_now)
    cachethq_metrics_add_point('Cachet_token', 2, item_value, timestamp_now[0:10])


if __name__ == "__main__":
    run_main()
