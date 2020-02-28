#!/usr/bin/env python
# encoding: utf-8
"""
@author: Jerry Lee
@license: (C) Copyright 2013-2019, Node Supply Chain Manager Corporation Limited.
@file: emailer.py
@time: 2020/1/2 5:25 下午
@desc:
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EMailer(object):
    def __init__(self, account, passwd, smtp_server):
        self.account = account
        self.passwd = passwd
        self.smtp_server = smtp_server

    def send(self, subject, mailto, content, attachments=None):
        #创建一个带附件的实例
        msg = MIMEMultipart()

        textmsg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg.attach(textmsg)

        #构造附件1
        if not attachments == None:
            for attachment in attachments:
                att1 = MIMEText(open(attachment, 'rb').read(), 'base64', 'utf-8')
                att1['Content-Type'] = 'application/octet-stream'
                filename = os.path.basename(attachment)
                description = 'attachment; filename=%s' % (filename,)
                att1['Content-Disposition'] = description #这里的filename可以任意写，写什么名字，邮件中显示什么名字
                msg.attach(att1)


        #加邮件头
        msg['to'] = ",".join(mailto)
        msg['from'] = self.account
        msg['subject'] = subject

        #发送邮件
        try:
            server = smtplib.SMTP()
            #server.set_debuglevel(1)
            server.connect(self.smtp_server)
            server.login(self.account, self.passwd)#XXX为用户名，XXXXX为密码
            server.sendmail(msg['from'], mailto, msg.as_string())
            server.quit()
            print('发送成功')
        except Exception as e:
            print(str(e))
