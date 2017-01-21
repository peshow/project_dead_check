# -*- coding:utf-8 -*-
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
    def generate_subject(self, process_name, is_ok=False):
        subject = "{} to be a zombie".format(process_name)
        if is_ok:
            subject = "{} return to OK".format(process_name)
        return subject

    def generate_mail_body(self, process_name=None, is_ok=False):
        body = "{} had become a dead process".format(process_name)
        if is_ok:
            body = "{} had return to running".format(process_name)
        mail_body = '''
        IP: {ip}
        Date: {date}
        Content: {body}'''.format(ip=IP, date=DATE, body=body)
        return mail_body

    def generate_dict(self, process):
        dictionary = {
            "error_subject": self.generate_subject(process),
            "error_body": self.generate_mail_body(process),
            "ok_subject": self.generate_subject(process, is_ok=True),
            "ok_body": self.generate_mail_body(process, is_ok=True)
        }
        return dictionary
