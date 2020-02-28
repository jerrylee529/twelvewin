#!/usr/bin/env python
# encoding: utf-8
"""
@author: Jerry Lee
@license: (C) Copyright 2013-2019, Node Supply Chain Manager Corporation Limited.
@file: sms_informer.py
@time: 2020/1/17 2:03 下午
@desc:
"""

from twilio.rest import Client
import os


class SMSInformer(object):
    def __init__(self):
        self.accountSID = os.environ['SMS_ACCOUNT_SID']
        self.authToken = os.environ['SMS_AUTH_TOKEN']
        self.myNumber = os.environ['SMS_MY_NUMBER']
        self.twilioNumber = os.environ['SMS_TWILIO_NUMBER']

    def inform(self, subject, content):
        twilioCli = Client(self.accountSID, self.authToken)

        message = "{} {}".format(subject, content)
        twilioCli.messages.create(body=message, from_=self.twilioNumber, to=self.myNumber)


if __name__ == '__main__':
    sms_sender = SMSInformer()
    sms_sender.inform('hell', 'the world')
