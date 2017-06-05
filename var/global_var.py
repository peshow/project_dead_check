import os
import pytz
import socket
import datetime
import logging
from subprocess import Popen, PIPE, STDOUT

BASE_DIR = os.path.dirname(os.path.abspath(__name__))


def log_settings(logname):
    path = os.path.join(BASE_DIR, logname)
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


class GetTimeMixIn:
    @staticmethod
    def get_current_time():
        """
        获取当前的时间字符串
        """
        tm_format = "%Y-%m-%d %H:%M:%S"
        tz = pytz.timezone("Asia/Shanghai")
        now = tz.localize(datetime.datetime.now())
        current_time = now.strftime(tm_format)
        return current_time


class ExecuteMixin:
    executes = None

    def operation(self):
        if self.executes is not None:
            with Popen(["/bin/bash", "-lc", "{}".format(self.executes)],
                       stdout=PIPE,
                       stderr=STDOUT,
                       start_new_session=True) as exe:
                code = exe.wait(30)
                out, *_ = exe.communicate()
                if code == 0:
                    self.logging.info("[{}] executes命令执行成功".format(self.project))
                else:
                    self.logging.warning("[{}] executes命令执行失败".format(self.project))


IP = get_ip()

