#!/usr/bin/env python
# encoding: utf-8
"""
@author: Jerry Lee
@license: (C) Copyright 2013-2019, Node Supply Chain Manager Corporation Limited.
@file: mail_informer.py
@time: 2020/1/2 6:34 下午
@desc: 邮件消息通知
"""

import os
try:
    from .emailer import EMailer
except:
    from emailer import EMailer


class MailInformer(object):
    def __init__(self):
        self.mail_account = os.environ['MAIL_ACCOUNT']
        self.mail_passwd = os.environ['MAIL_PASSWD']
        self.smtp_server = os.environ['SMTP_SERVER']
        self.mail_address_to = os.environ['MAIL_ADDRESS_TO']

        self.mailer = EMailer(self.mail_account, self.mail_passwd, self.smtp_server)

    def inform(self, subject, content):
        self.mailer.send(subject, mailto=self.mail_address_to, content=content)


if __name__ == '__main__':
    mailer = MailInformer()

    mailer.inform('测试', 'test')
