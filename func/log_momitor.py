import os
import re
from datetime import timedelta, datetime
from collections import deque
from sendmail import SendEmail
from conf.email_var import GenerateMonitorVar


class LogMonitor:
    def __init__(self, files, patterns, mail_build_func,
                 auto_cut=True,
                 time_format=".%Y-%m-%d",
                 behind=2):
        self.__files = files
        self.patterns = patterns.split(",")
        self.mail_build_func = mail_build_func
        self.__cursor = os.path.getsize(files)
        self.deque = deque(maxlen=3)
        self.number = self.behind = behind
        self.time_format = time_format
        self.auto_cut = auto_cut
        self.file_exists = 0
        self.send_mail = SendEmail()

    def __read_file(self):
        try:
            with open(self.__files) as f:
                if os.path.getsize(self.__files) < self.__cursor and self.auto_cut:
                    with open(self.cut()) as f_prev:
                        f_prev.seek(self.__cursor)
                        yield from f_prev
                f.seek(self.__cursor)
                yield from f
                self.__cursor = f.tell()
                self.file_exists = 0
        except FileNotFoundError:
            self.file_exists += 1
            print(self.file_exists)
            if self.file_exists > 3:
                print("File is NotFound")

    def parse_and_send(self):
        for line in self.__read_file():
            if self.number < self.behind:
                self.deque.append(line)
                self.number += 1
                if self.number == self.behind:
                    self.send()
                    self.__cursor = os.path.getsize(self.__files)
                    return
                continue
            for pattern_t in self.patterns:
                pattern = re.compile(pattern_t)
                m = pattern.search(line)
                print(m)
                if m:
                    self.number = 0
                    self.deque.append(line)

    def cut(self):
        yesterday = datetime.today() - timedelta(days=1)
        prev_date = yesterday.strftime(self.time_format)
        pre_file = self.__files + prev_date
        return pre_file

    def send(self):
        dictionary = self.mail_build_func.generate_dict("".join(self.deque))
        self.send_mail.build_mail(**dictionary)
        self.send_mail.send()



