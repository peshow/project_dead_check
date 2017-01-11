import os
import sys
import threading
from datetime import datetime, timedelta
from sendmail import sendmail
from pyhocon import ConfigFactory


Event = threading.Event()
conf = ConfigFactory.parse_file("conf/mail.conf")


class CheckDead:
    def __init__(self, delta=15):
        self.delta = delta
        self.previous_time = None
        self.previous_size = None
        self.first = False
        self.logfile = conf.get("thread.logfile")

    def check(self, logfile):
            if not self.first:
                self.previous_size = os.path.getsize(logfile)
                self.previous_time = datetime.now()
                self.first = True
                Event.wait(5)
            while not Event.is_set():
                size = os.path.getsize(logfile)
                now = datetime.now()
                if size == self.previous_size:
                    print("{} is not change".format(self.logfile))
                    delta = now - self.previous_time
                    print(self.previous_time, delta, timedelta(seconds=self.delta))
                    if delta > timedelta(seconds=self.delta):
                        self.send_email()
                        print("email send Ok")
                        Event.wait(60)
                else:
                    print(size, self.previous_size)
                    self.previous_time = now
                Event.wait(5)

    def send_email(self):
        src = conf.get("email.src")
        password = conf.get("email.password")
        recipients = conf.get("email.recipients")
        mail_body = "{} is death, now will restart project".format(self.name)
        sendmail(mail_body, src, recipients, password)


class MultiThreading:
    def __init__(self):
        self.file_list = conf.get("thread.logfile")

    def start_thread(self):
        for logfile in self.file_list:
            checkDead = CheckDead()
            t = threading.Thread(target=checkDead.check, name=os.path.basename(logfile), args=(logfile,))
            t.start()

if __name__ == "__main__":
    try:
        multi = MultiThreading()
        multi.start_thread()
    except KeyboardInterrupt:
        Event.set()