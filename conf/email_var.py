# -*- coding:utf-8 -*-
import os
import socket
import datetime
import pytz


def get_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        address, port = sock.getsockname()
        sock.close()
        return address
    except socket.error:
        return "127.0.0.1"


def get_current_time():
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
        self.subject= subject
        self.process_name = process_name
        self.recipients = recipients

    def edit_subject(self):
        return self.subject.format(self.process_name)

    def generate_mail_body(self, body):
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
        dictionary = {
            "subject": self.edit_subject(),
            "mail_body": self.generate_mail_body(body),
            "recipients": self.recipients
        }
        return dictionary
