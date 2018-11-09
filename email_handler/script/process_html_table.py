#!/usr/bin/python3
# -*- coding=utf-8 -*-

from bs4 import BeautifulSoup


class ProcessHtmlTable:
    def __init__(self, html_content):
        self.html_content = html_content

    def process_table(self):
        soup = BeautifulSoup(self, 'lxml')

        msg = ''
        for row in soup.find_all('tr'):
            msg = msg + row.get_text(',', strip=True) + '\n'
        return msg
