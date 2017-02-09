# -*- coding:utf-8 -*-
import os
import socket
import datetime
import pytz


def get_ip():
    """
    获取本机的IP地址(Get IP Address of the local host)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        address, port = sock.getsockname()
        sock.close()
        return address
    except socket.error:
        return "127.0.0.1"


def get_current_time():
    """
    获取当前的时间字符串
    """
    tm_format = "%Y-%m-%d %H:%M:%S"
    tz = pytz.timezone("Asia/Shanghai")
    now = tz.localize(datetime.datetime.now())
    current_time = now.strftime(tm_format)
    return current_time

IP = get_ip()
DATE = get_current_time()


class GenerateEmailVar:
    def __init__(self, process_name, ok_subject=None, ok_body=None, error_subject=None, error_body=None):
        self.ok_subject = ok_subject
        self.ok_body = ok_body
        self.error_body = error_body
        self.error_subject = error_subject
        self.process_name = process_name

    def generate_subject(self, is_ok=False):
        subject = self.error_subject.format(self.process_name)
        if is_ok:
            subject = self.ok_subject.format(self.process_name)
        return subject

    def generate_mail_body(self, is_ok=False):
        body = self.error_body.format(self.process_name)
        if is_ok:
            body = self.ok_body.format(self.process_name)
        mail_body = '''
        <p><strong>IP:</strong> {ip}</p>
        <p><strong>Date:</strong> {date}<p>
        <p><strong>Project:</strong> {process_name}<p>
        <strong>Content:</strong>
        <pre>{body}</pre>'''.format(ip=IP,
                                    date=DATE,
                                    process_name=self.process_name,
                                    body=body)
        return mail_body

    def generate_dict(self):
        dictionary = {
            "error_subject": self.generate_subject(),
            "error_body": self.generate_mail_body(),
            "ok_subject": self.generate_subject(is_ok=True),
            "ok_body": self.generate_mail_body(is_ok=True)
        }
        return dictionary


class GenerateMonitorVar:
    def __init__(self, subject=None, process_name=None, recipients=None):
        """
        生成日志异常信息监控的'标题,正文,收件人列表'
        :param subject: 邮件发送的标题
        :param process_name: 处理的进程名称
        :param recipients: 邮件发送人列表，必须是以逗号分隔的string
        """
        self.subject= subject
        self.process_name = process_name
        self.recipients = recipients

    def edit_subject(self):
        return self.subject.format(self.process_name)

    def generate_mail_body(self, body):
        """
        日志异常信息的正文需要接收
        检索到的异常信息，因此将该
        函数传递到log_monitor， 接
        收body参数
        """
        mail_body = '''
        <p><strong>IP:</strong> {ip}</p>
        <p><strong>Date:</strong> {date}<p>
        <p><strong>Project:</strong> {process_name}<p>
        <strong>Content:</strong>
        <pre>{body}</pre>'''.format(ip=IP,
                                    date=DATE,
                                    process_name=self.process_name,
                                    body=body)
        return mail_body

    def generate_dict(self, body):
        """
        :param body: 传递检索到的错误信息生成邮件正文
        :return: 返回邮件发送所需的标题、正文、收件人列表
        """
        dictionary = {
            "subject": self.edit_subject(),
            "mail_body": self.generate_mail_body(body),
            "recipients": self.recipients
        }
        return dictionary
