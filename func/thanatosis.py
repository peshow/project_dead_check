import os
import re
import time
import psutil 
from sendmail import SendEmail
from var.dead_var import EmailMixIn
from var.global_var import log_settings, ExecuteMixin


class CheckRunning:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self

        # @wraps(self.func)
        def stash(*args, **kwargs):
            command = re.compile(instance.command)
            is_running = False
            for prc in psutil.process_iter():
                cmd = " ".join(prc.cmdline())
                if command.search(cmd):
                    is_running = True
            if is_running:
                result = self.func(instance, *args, **kwargs)
                return result
            else:
                instance.logging.warning("[{}] is not running!".format(instance.command))
        return stash


class CheckDead(EmailMixIn, ExecuteMixin):
    def __init__(self, project, log_path, counts_send, command,
                 mail_body=None, recipients=None, executes=None, delay=60):
        """
        根据日志文件的ctime和size的变化，判断进程是否假死
        :param log_path: 日志文件位置
        :param counts_send: 错误邮件发送次数
        :param delay: 判断ctime未变化的时间间隔
        :param mail_body: 邮件主体
        :param recipients: 邮件发送人列表
        """
        self.project = project
        self.log_path = log_path
        self.counts_send = counts_send
        self.command = command
        self.mail_body = mail_body
        self.recipients = recipients
        self.executes = executes
        self.delay = delay
        self.previous_size = os.path.getsize(log_path)
        self.previous_ctime = os.path.getctime(log_path)
        self.__is_first_run = True
        self.logging = log_settings("log/dead_monitor.log")
        self.send_mail = SendEmail()

    def __check_is_first(self):
        """
        判断是否是第一次执行
        """
        if self.__is_first_run:
            self.__is_first_run = False
            time.sleep(3)
            return True

    def check_size_change(self):
        """
        检查文件大小是否发生变更
        """
        size = os.path.getsize(self.log_path)
        diff_value = size - self.previous_size
        if diff_value == 0:
            self.logging.info("[{}] size is not change".format(self.project))
            return True
        self.previous_size = size
        return

    def check_ctime_change(self):
        """
        检查文件ctime是否发生变化
        """
        now = os.path.getctime(self.log_path)
        delay = now - self.previous_ctime
        if delay == 0:
            self.logging.info("[{}] ctime is not change".format(self.project))
            return True
        self.previous_ctime = now
        return

    @CheckRunning
    def main_check(self, interval=30):
        """
        进程假死检测主函数
        """
        if self.__check_is_first():
            return
        if not self.error_is_send and self.check_ctime_change() or self.check_size_change():
            self.error_send()
            while True:
                self.operation()
                if self.check_ctime_change() is None or self.check_size_change() is None:
                    self.logging.info("[{}] is normal operation".format(self.project))
                    self.ok_send()
                    break
                time.sleep(interval)

