import os
import time
from datetime import datetime
from sendmail import SendEmail


class CheckDead:
    def __init__(self, log_path, counts_send, delay=60, mail_body=None, recipients=None):
        """
        根据日志文件的ctime和size的变化，判断进程是否假死
        :param log_path: 日志文件位置
        :param counts_send: 错误邮件发送次数
        :param delay: 判断ctime未变化的时间间隔
        :param mail_body: 邮件主体
        :param recipients: 邮件发送人列表
        """
        self.log_path = log_path
        self.counts_send = counts_send
        self.mail_body = mail_body
        self.recipients = recipients
        self.delay = delay
        self.previous_size = os.path.getsize(log_path)
        self.previous_ctime = os.path.getctime(log_path)
        self.__is_first_run = True
        self.current_counts_error_send = 0
        self.__error_is_send = False
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
            print("size not change")
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
            print("time not change")
            return True
        self.previous_ctime = now
        return

    def main_check(self):
        """
        进程假死检测主函数
        """
        if self.__check_is_first():
            return
        if self.check_ctime_change() or self.check_size_change():
            self.__error_send()
        else:
            print("return is_ok\n")
            self.__ok_send()

    def __error_send(self):
        """
        发送异常邮件
        """
        print(self.current_counts_error_send, self.counts_send)
        if self.current_counts_error_send < self.counts_send:
            self.current_counts_error_send += 1
            self.__error_is_send = True
            self.send_mail.build_mail(self.mail_body["error_body"],
                                      self.mail_body["error_subject"],
                                      self.recipients)
            self.send_mail.send()
            print("error {} send".format(self.log_path), self.__error_is_send)

    def __ok_send(self):
        """
        发送返回正常邮件
        """
        if self.__error_is_send:
            self.current_counts_error_send = 0
            self.__error_is_send = False
            self.send_mail.build_mail(self.mail_body["ok_body"],
                                      self.mail_body["ok_subject"],
                                      self.recipients)
            self.send_mail.send()
            print("return ok {} send".format(self.log_path), self.__error_is_send)



# class MultiThreading:
#     def __init__(self):
#         self.file_list = conf.get("thread.logfile")
#
#     def start_thread(self):
#         for logfile in self.file_list:
#             checkDead = CheckDead()
#             t = threading.Thread(target=checkDead.main_check, name=os.path.basename(logfile), args=(logfile,))
#             t.start()
#
# if __name__ == "__main__":
#     try:
#         multi = MultiThreading()
#         multi.start_thread()
#     except KeyboardInterrupt:
#         Event.set()
