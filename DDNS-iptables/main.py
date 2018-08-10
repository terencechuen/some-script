#!/usr/sbin/python3

import dns.resolver as resolver
import subprocess, sys, json


# 读取配置文件
def read_config():
    config_content = open(sys.path[0] + '/config.json')
    try:
        config_json = json.loads(config_content.read())
    except Exception as e:
        print('config json error, load failed! msg: \n' + str(e))
        sys.exit(1)
    else:
        config_content.close()
        return config_json


# 从iptables INPUT链中检索包含 "DDNS iptables rule" 备注的规则
def get_info_from_chain():
    shell_get_rules = 'iptables -L INPUT -n --line-numbers | grep "DDNS iptables rule"'
    output_dict = dict()

    run_shell = subprocess.Popen(shell_get_rules, shell=True, stdout=subprocess.PIPE)
    shell_output = run_shell.communicate()[0]

    # 判断status code，若无相关规则，则返还status code 1，此时直接返还空字典
    if run_shell.returncode == 1:
        return output_dict
    # 判断status code，若有相关规则，则返还status code 0，此时返还经过处理的字典
    elif run_shell.returncode == 0:
        output_list = shell_output.decode().split('\n')
        for i in output_list:
            if len(i) == 0:
                pass
            else:
                i_list = ' '.join(i.split()).split()
                output_dict[i_list[4]] = i_list[0]
        return output_dict

    # 若返还的status code不是0或1，则抛出异常
    else:
        raise subprocess.CalledProcessError(run_shell.returncode, shell_get_rules, output=shell_output)


# 往INPUT链插入规则
def append_rule_to_chain(src_ip, dst_port, proto):
    shell_append_rule = 'iptables -A INPUT -p ' + str(proto) + ' --dport ' + str(dst_port) + ' -s ' + str(
        src_ip) + ' -j ACCEPT -m comment --comment "DDNS iptables rule"'

    run_shell = subprocess.Popen(shell_append_rule, shell=True, stdout=subprocess.PIPE)
    shell_output = run_shell.communicate()[0]

    if run_shell.returncode == 0 or 1:
        pass
    else:
        raise subprocess.CalledProcessError(run_shell.returncode, shell_append_rule, output=shell_output)


# 从INPUT链中删除规则
def del_rule_from_chain(rule_id):
    shell_del_rule = 'iptables -D INPUT ' + str(rule_id)

    run_shell = subprocess.Popen(shell_del_rule, shell=True, stdout=subprocess.PIPE)
    shell_output = run_shell.communicate()[0]

    if run_shell.returncode == 0 or 1:
        pass
    else:
        raise subprocess.CalledProcessError(run_shell.returncode, shell_del_rule, output=shell_output)


# 从DNS服务器获取特定解析类型的IP地址
def get_dns_record(ddns_domain, ddns_record):
    output_list = []
    dns_resolver = resolver.Resolver()
    dns_answers = dns_resolver.query(ddns_domain, ddns_record)
    if len(dns_answers) is not 0:
        for rdata in dns_answers:
            output_list.append(str(rdata))
    return output_list


if __name__ == '__main__':
    config_dict = read_config()  # 读取配置文件
    dns_list = get_dns_record(config_dict['domain'], config_dict['record'])  # 获取IP地址列表
    dns_list_need_remove = []  # 建立中间列表
    chain_dict = get_info_from_chain()  # 获取现有规则

    '''
    1. 遍历DNS解析记录：遍历故障转移环境中多个IP地址
    2. 逐一比对iptables中的记录，若比对成功，则从chain_dict字典中删除key，否则调用append_rule_to_chain函数
    '''
    for j in dns_list:
        if j in chain_dict.keys():
            del chain_dict[j]
        else:
            append_rule_to_chain(j, config_dict['port'], config_dict['proto'])

    # 读取chain_dict字典中所有value，也就是iptables规则的编号
    rule_id_list = list(chain_dict.values())

    # 如果rule_id_list列表中的value数量大于1，则调用sorted排序，降序
    if len(rule_id_list) > 1:
        rule_id_list = sorted(rule_id_list, reverse=True)

    # 遍历排序后的rule_id_list列表，调用del_rule_from_chain参数逐一删除失效的INPUT规则
    for i in rule_id_list:
        del_rule_from_chain(i)
