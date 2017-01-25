import os
import time
from datetime import datetime
from sendmail import SendEmail


class CheckDead:
    def __init__(self, mail_body=None, recipients=None, delta=60):
        self.delta = delta
        self.previous_time = None
        self.previous_size = None
        self.__first = True
        self.times = 0
        self.SendEmail = SendEmail()
        self.mail_body = mail_body
        self.recipients = recipients
        self.__is_send = False
        self.public = None

    def __is_first(self, logfile):
        if self.__first:
            self.previous_size = os.path.getsize(logfile)
            self.previous_time = datetime.now().timestamp()
            self.__first = False
            time.sleep(5)

    def check(self, logfile, times=1):
        self.public = logfile
        self.__is_first(logfile)
        size = os.path.getsize(logfile)
        now = datetime.now().timestamp()
        if size == self.previous_size:
            delta = now - self.previous_time
            print("{} is not change".format(logfile), delta, delta > self.delta)
            if delta > self.delta:
                self.__error_send(times)
        else:
            print("{} is write".format(logfile), self.__first)
            if self.__is_send:
                self.__ok_send()
            self.previous_time = now
            self.previous_size = size

    def __error_send(self, times):
        if self.times < times:
            self.SendEmail.build_mail(self.mail_body["error_body"],
                                      self.mail_body["error_subject"],
                                      self.recipients)
            self.SendEmail.send()
            self.times += 1
            self.__is_send = True
            print("{} send".format(self.public), self.__is_send)

    def __ok_send(self):
        self.SendEmail.build_mail(self.mail_body["ok_body"],
                                  self.mail_body["ok_subject"],
                                  self.recipients)
        self.SendEmail.send()
        self.__is_send = False
        print("{} send".format(self.public), self.__is_send)



# class MultiThreading:
#     def __init__(self):
#         self.file_list = conf.get("thread.logfile")
#
#     def start_thread(self):
#         for logfile in self.file_list:
#             checkDead = CheckDead()
#             t = threading.Thread(target=checkDead.check, name=os.path.basename(logfile), args=(logfile,))
#             t.start()
#
# if __name__ == "__main__":
#     try:
#         multi = MultiThreading()
#         multi.start_thread()
#     except KeyboardInterrupt:
#         Event.set()
