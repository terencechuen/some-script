#!/usr/bin/python3
# -*- coding=utf-8 -*-

import email
import email.header
import imaplib
import os
import re
import sys
from datetime import datetime

from script.process_html_table import ProcessHtmlTable

# 定义目录
local_path = sys.path[0]
config_path = local_path + '/config.json'

# 检查配置文件
if os.path.exists(config_path):
    r = open(config_path, 'r')
    r_read = r.readlines()
    r.close()
    config_json = ''
    for i in r_read:
        config_json = config_json + i

    config_json = eval(config_json)
else:
    print("config file is not exists!")
    sys.exit(0)

# 邮件配置
imap_host = config_json['email']['host']
imap_port = config_json['email']['port']
imap_username = config_json['email']['username']
imap_passwd = config_json['email']['passwd']

comm = imaplib.IMAP4_SSL(imap_host, imap_port)
comm.login(imap_username, imap_passwd)
# print(comm.list())

mail_folder = ['INBOX/NGXProj&eyxOjGcfYr1ZVm07Uqg-']


# 获取邮件uid
def get_uid_list(folder_name):
    comm.select(folder_name)
    response, uid_list = comm.uid('search', None, 'ALL')
    uid_list = uid_list[0].decode().split(' ')
    return uid_list


# 获取邮件
def get_mail_data(folder_name, mail_uid):
    comm.select(folder_name)
    response, mail_data = comm.fetch(mail_uid, '(RFC822)')
    mail_data = email.message_from_string(mail_data[0][1].decode())
    msg_content = email.header.decode_header(mail_data['Subject'])
    print(msg_content)
    return mail_data


# 获取日期
today_date = datetime.today().date()
today_date = str(today_date).replace('-', '_')

# 定义目录
local_path = sys.path[0]
data_store_dir = local_path + '/datastore/' + today_date + '/'

for i in mail_folder:
    mail_content_dir = data_store_dir + i
    if os.path.exists(mail_content_dir):
        if not os.path.exists(mail_content_dir):
            os.mkdir(mail_content_dir)
    else:
        os.makedirs(mail_content_dir)


# 保存邮件
def write_content_to_file(folder, mail_id, file_content):
    file_path = data_store_dir + folder + '/' + str(mail_id) + '.eml'
    file_content = file_content[0][1].decode()
    file_content = email.message_from_string(file_content)
    j_file = open(file_path, 'w')
    j_file.write(str(file_content))
    j_file.close()


# 写入日志
def write_log_to_file(folder, mail_uid):
    file_path = local_path + '/' + '.temp.log'
    if os.path.exists(file_path):
        if os.path.getsize(file_path):
            f = open(file_path, 'r')
            f_dict = f.readline()
            f_dict = eval(f_dict)
            f_dict[folder] = mail_uid
            f = open(file_path, 'w')
            f.write(str(f_dict))
            f.close()
        else:
            f_dict = dict()
            f = open(file_path, 'w')
            f_dict[folder] = mail_uid
            f.write(str(f_dict))
            f.close()
    else:
        f_dict = dict()
        f = open(file_path, 'w')
        f_dict[folder] = mail_uid
        f.write(str(f_dict))
        f.close()


def check_last_mail_uid(folder, mail_uid):
    file_path = local_path + '/' + '.temp.log'
    if os.path.exists(file_path):
        if os.path.getsize(file_path):
            log_dict = open(file_path, 'r')
            log_dict = log_dict.readline()
            log_dict = eval(str(log_dict))
            if folder in log_dict:
                j = log_dict[folder]
                if int(mail_uid) > int(j):
                    return True, j
                else:
                    return False, True
            else:
                return False, False
        else:
            return False, None
    else:
        return None, None


def get_charset(content):
    re_pattern = re.compile(r'charset\=.*')
    mail_charset = re_pattern.findall(content)[0]
    mail_charset = mail_charset.split('=')[1]
    mail_charset = mail_charset.lower()
    return mail_charset


def check_table(email_content):
    re_pattern = re.compile(r'<html>|<tr>|<td>')
    re_count = len(re_pattern.findall(email_content))
    if re_count >= 4:
        return True
    else:
        return False


def process_mail_content(content):
    j = content[0][1].decode()
    j = email.message_from_string(j)
    mail_charset = get_charset(str(j))
    f = ''
    for f in j.walk():
        if f.get_content_type():
            f = f.get_payload(decode=True)
    f = f.decode(mail_charset)
    if check_table(f):
        f = ProcessHtmlTable.process_table(f)
    return f


for i in mail_folder:
    mail_uid_list = get_uid_list(i)
    mail_uid_new = mail_uid_list[-1]
    check_mail = check_last_mail_uid(i, mail_uid_new)
    check_mail_data_check = check_mail[0]
    check_mail_value = check_mail[1]
    if check_mail_data_check:
        mail_uid_old = int(check_mail_value)
        while mail_uid_old < int(mail_uid_new):
            mail_uid_old += 1
            mail_content = get_mail_data(i, str(mail_uid_old))
            if mail_content[0] is None:
                pass
            else:
                write_content_to_file(i, mail_uid_old, mail_content)
                write_log_to_file(i, mail_uid_old)
    elif check_mail_data_check is None:
        for k in mail_uid_list:
            mail_content = get_mail_data(i, k)
            if mail_content[0] is None:
                pass
            else:
                write_content_to_file(i, k, mail_content)
                write_log_to_file(i, k)
    else:
        if check_mail_value:
            pass
        elif check_mail_value is None:
            for k in mail_uid_list:
                mail_content = get_mail_data(i, k)
                if mail_content[0] is None:
                    pass
                else:
                    write_content_to_file(i, k, mail_content)
                    write_log_to_file(i, k)
        else:
            file_path = local_path + '/' + '.temp.log'
            for k in mail_uid_list:
                mail_content = get_mail_data(i, k)
                if mail_content[0] is None:
                    pass
                else:
                    write_content_to_file(i, k, mail_content)
                    j = open(file_path, 'r')
                    log_dict = j.readline()
                    log_dict = eval(log_dict)
                    log_dict[i] = k
                    j = open(file_path, 'w')
                    j.write(str(log_dict))
                    j.close()

comm.logout()
