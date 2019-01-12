#!/usr/bin/python3
# -*- coding=utf-8 -*-

import email
import email.header
import imaplib
import os
import sys
from datetime import datetime

# 定义目录
local_path = sys.path[0]

# 邮箱账户信息配置文件
config_path = local_path + '/config.json'

# 读取配置文件
r_conf = open(config_path, 'r')
config_content = r_conf.read()
r_conf.close()

# 格式化配置文件
config_json = eval(config_content)

# 邮件配置
imap_host = config_json['email']['host']
imap_port = config_json['email']['port']
imap_username = config_json['email']['username']
imap_passwd = config_json['email']['passwd']
subj_prefix = config_json['subj_prefix']
subj_count = config_json['subj_count']

# 通过IMAP登入邮箱服务器
comm = imaplib.IMAP4_SSL(imap_host, imap_port)
comm.login(imap_username, imap_passwd)

# 获取邮箱文件夹列表
# print(comm.list())

# 定义邮箱文件夹，list格式
mail_folder = ['INBOX/NGXProj&eyxOjGcfYr1ZVm07Uqg-']


# 获取邮件uid
def get_uid_list(folder_name):
    comm.select(folder_name)
    response, uid_list = comm.uid('search', None, 'ALL')
    print(uid_list)
    uid_list = uid_list[0].decode().split(' ')
    print(uid_list)
    return uid_list


# 获取邮件内容与标题（subject）
def get_mail_data(folder_name, mail_uid):
    comm.select(folder_name)
    response, mail_data = comm.uid('fetch', mail_uid, '(RFC822)')

    mail_data = email.message_from_string(mail_data[0][1].decode())

    msg_subj = email.header.decode_header(mail_data['Subject'])
    msg_subj = msg_subj[0][0].decode(msg_subj[0][1])

    msg_sender = email.header.decode_header(mail_data['From'])

    if len(msg_sender) == 1:
        msg_sender = msg_sender[0][0].strip("'").split('<')[1][:-1]
    elif len(msg_sender) == 2:
        msg_sender = msg_sender[1][0].decode()[2:-1]
    else:
        msg_sender = msg_sender[2][0].decode()[2:-1]

    return mail_data, msg_subj, msg_sender


# 获取日期
today_date = datetime.today().date()
today_date = str(today_date).replace('-', '_')

# 定义目录，用于存储邮件数据
data_store_dir = local_path + '/datastore/' + today_date + '/'

# 建立数据存储目录
for i_folder_name in mail_folder:
    mail_content_dir = data_store_dir + i_folder_name
    if os.path.exists(mail_content_dir):
        if not os.path.exists(mail_content_dir):
            os.mkdir(mail_content_dir)
    else:
        os.makedirs(mail_content_dir)


# 邮件保存函数
def write_content_to_file(folder, mail_id, file_content):
    mail_file_path = data_store_dir + folder + '/' + str(mail_id) + '.eml'
    w_file = open(mail_file_path, 'w')
    w_file.write(str(file_content))
    w_file.close()


# 日志文件路径
log_file_path = local_path + '/temp.log'


# 写入日志（N年前的代码片段，能用，但无心修改）
def write_log_to_file(folder, mail_uid):
    if os.path.exists(log_file_path):
        if os.path.getsize(log_file_path):
            f = open(log_file_path, 'r')
            f_dict = f.readline()
            f_dict = eval(f_dict)
            f_dict[folder] = mail_uid
            f = open(log_file_path, 'w')
            f.write(str(f_dict))
            f.close()
        else:
            f_dict = dict()
            f = open(log_file_path, 'w')
            f_dict[folder] = mail_uid
            f.write(str(f_dict))
            f.close()
    else:
        f_dict = dict()
        f = open(log_file_path, 'w')
        f_dict[folder] = mail_uid
        f.write(str(f_dict))
        f.close()


# 检查邮件uid是否已经存在
def check_last_mail_uid(folder, mail_uid):
    temp_file_path = local_path + '/' + '.temp.log'
    try:
        temp_content = open(temp_file_path, 'r')
    except FileNotFoundError:
        return None, 0
    else:
        temp_content = temp_content.read()
        temp_dict = eval(str(temp_content))
        if folder in temp_dict:
            mail_old_uid = temp_dict[folder]
            if int(mail_uid) > int(mail_old_uid):
                return True, mail_old_uid
            else:
                return False, 0
        else:
            return None, 0


# 格式化邮件标题，输出QQ号码与奖品列表
def format_subj(mail_subj):
    mail_subj_list = mail_subj.split('/')
    if mail_subj_list[0] == subj_prefix and len(mail_subj_list) == 3:
        applicant_id = mail_subj_list[1]
        subj_id_list = list(mail_subj_list[2])
        return applicant_id, subj_id_list
    else:
        return False


# 输出csv文件
def csv_output(mail_sender, applicant_id, subj_id_list):
    csv_output_front_part = mail_sender + ',' + applicant_id + ','
    count_start = 1
    while subj_count + 1 > count_start:
        if str(count_start) in subj_id_list:
            csv_output_front_part += 'True,'
        else:
            csv_output_front_part += 'False,'
        count_start += 1

    csv_file_path = local_path + '/output.csv'

    if os.path.exists(csv_file_path):
        csv_output_content = csv_output_front_part[:-1] + '\n'
    else:
        first_row_front_part = 'mail_sender' + ',' + 'applicant_id' + ','
        count_start = 1
        while subj_count + 1 > count_start:
            first_row_front_part += str(count_start) + ','
            count_start += 1
        csv_output_content = first_row_front_part[:-1] + '\n' + csv_output_front_part[:-1] + '\n'

    w_csv = open(csv_file_path, 'a')
    w_csv.write(csv_output_content)
    w_csv.close()


def run():
    for i in mail_folder:
        mail_uid_list = get_uid_list(i)
        mail_uid_new = mail_uid_list[-1]
        check_mail = check_last_mail_uid(i, mail_uid_new)
        check_mail_uid = check_mail[0]
        check_mail_value = check_mail[1]

        # 该uid较temp文件中的大，说明有新邮件
        if check_mail_uid:
            mail_uid_old = int(check_mail_value)
            while mail_uid_old < int(mail_uid_new):
                mail_content = get_mail_data(i, str(mail_uid_old))
                format_subj_tube = format_subj(mail_content[1])

                if mail_content[0] is None or format_subj_tube is False:
                    write_log_to_file(i, mail_uid_old)
                else:
                    write_content_to_file(i, mail_uid_old, mail_content[0])
                    csv_output(mail_content[2], format_subj_tube[0], format_subj_tube[1])
                    write_log_to_file(i, mail_uid_old)
                mail_uid_old += 1
        # 临时文件不存在或临时文件中没有相关邮件文件夹的key，说明从未下载过邮件
        elif check_mail_uid is None:
            for k in mail_uid_list:
                mail_content = get_mail_data(i, k)
                format_subj_tube = format_subj(mail_content[1])

                if mail_content[0] is None or format_subj_tube is False:
                    write_log_to_file(i, k)
                else:
                    write_content_to_file(i, k, mail_content[0])
                    csv_output(mail_content[2], format_subj_tube[0], format_subj_tube[1])
                    write_log_to_file(i, k)
        # uid与临时文件中的值一致，说明无新邮件
        else:
            pass


if __name__ == '__main__':
    run()
    comm.logout()
