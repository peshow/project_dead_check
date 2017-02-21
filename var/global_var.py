import os
import pytz
import socket
import datetime
import logging

def log_settings(logname):
    path = os.path.join(os.getcwd(), logname)
    print(path)
    logging.basicConfig(filename=path,
                        level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s [%(threadName)s] - %(message)s')
    return logging


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
