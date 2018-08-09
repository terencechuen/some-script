import dns.resolver as resolver
import subprocess


def get_info_from_chain():
    shell_get_rules = 'iptables -L INPUT -n --line-numbers | grep "DDNS iptables rule"'
    output_dict = dict()
    run_shell = subprocess.Popen(shell_get_rules, shell=True, stdout=subprocess.PIPE)
    msg, err = run_shell.communicate()
    if msg is None:
        if err is None:
            return output_dict
    else:
        output_list = msg.decode().split('\n')
        for i in output_list:
            if len(i) == 0:
                pass
            else:
                i_list = ' '.join(i.split()).split()
                output_dict[i_list[4]] = i_list[0]
    return output_dict


def get_dns_record():
    output_list = []
    dns_resolver = resolver.Resolver()
    dns_answers = dns_resolver.query('aliyun.com', 'A')
    if len(dns_answers) is not 0:
        for rdata in dns_answers:
            output_list.append(str(rdata))
    return output_list


def append_rule_to_chain(src_ip, dst_port, proto):
    shell_append_rule = 'iptables -A INPUT -p ' + str(proto) + ' --dport ' + str(dst_port) + ' -s ' + str(
        src_ip) + ' -j ACCEPT -m comment --comment "DDNS iptables rule"'
    subprocess.check_output(shell_append_rule, shell=True)


def del_rule_from_chain(rule_id):
    shell_del_rule = 'iptables -D INPUT ' + str(rule_id)
    subprocess.check_output(shell_del_rule, shell=True)


if __name__ == '__main__':
    dns_list = get_dns_record()
    print(dns_list)
    chain_dict = get_info_from_chain()

    for i in dns_list:
        if i in chain_dict.keys():
            del chain_dict[i]
        else:
            append_rule_to_chain(i, 80, 'tcp')

    if len(dns_list) == 0:
        pass
    else:
        for v in chain_dict.values():
            del_rule_from_chain(v)
