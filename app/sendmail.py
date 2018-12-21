# send mail
# -*- coding:utf-8 -*-
__author__ = 'jerry'

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import Encoders
from email import Utils
import os
import smtplib


#"突破60天均线的股票列表"

def send_mail(subject, mailto, content, attachments):

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
    msg['from'] = 'xxx@163.com'
    msg['subject'] = subject

    #发送邮件
    try:
        server = smtplib.SMTP()
        #server.set_debuglevel(1)
        server.connect('smtp.163.com')
        server.login('xxx', 'xxxxx')#XXX为用户名，XXXXX为密码
        server.sendmail(msg['from'], mailto, msg.as_string())
        server.quit()
        print '发送成功'
    except Exception, e:
        print str(e)

#sendmail('突破60天均线股票列表', content='突破60天均线股票列表', attachments=['C:/Stock/data/mafilter_60_20151128.txt'])
