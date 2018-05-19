import requests
import sys

req_msg = sys.argv[1]

ngx_status_url = 'http://ngx-status.ngx.hk/'

r = requests.get(ngx_status_url)
r_content = r.content.decode()
r_status_code = r.status_code

r_list = r_content.split('\n')


def get_value(req_str):
    if req_str == 'accepts':
        return_value = r_list[2].split(' ')[1]
    elif req_str == 'handled':
        return_value = r_list[2].split(' ')[2]
    elif req_str == 'requests':
        return_value = r_list[2].split(' ')[3]
    elif req_str == 'active':
        return_value = r_list[0].split(' ')[2]
    elif req_str == 'reading':
        return_value = r_list[3].split(' ')[1]
    elif req_str == 'writing':
        return_value = r_list[3].split(' ')[3]
    elif req_str == 'waiting':
        return_value = r_list[3].split(' ')[5]
    else:
        return_value = 'error'
    return return_value


if __name__ == '__main__':
    if r_status_code is not 200:
        print('')
    else:
        ngx_value = get_value(req_msg)
        if ngx_value == 'error':
            print('')
        else:
            print(ngx_value)
