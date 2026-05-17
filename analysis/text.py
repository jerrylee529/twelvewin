# coding=utf8

"""文本通知占位实现。

send_text() 当前只将消息打印到标准输出，供 quotation 等模块在异常时调用。
"""

__author__ = 'Administrator'

def send_text(msg):
    print(msg)
