import os
import re
from collections import deque
from sendmail import SendEmail
from datetime import timedelta, datetime


class LogMonitor:
    def __init__(self, files, patterns, mail_build_func,
                 auto_cut=True,
                 time_format=".%Y-%m-%d",
                 behind=2):
        """
        实现日志文件的增量监控，
        并可针对日志切割做处理
        :param files: 监控的日志文件路径
        :param patterns: 异常检索的正则匹配，以逗号分隔的字符串
        :param mail_build_func: 构建邮件内容的函数
        :param auto_cut: 是否启用日志切割
        :param time_format: 日志切割的事件格式
        :param behind: 取出匹配到异常后多少行
        """
        self.__files = files
        self.patterns = patterns.split(",")
        self.mail_build_func = mail_build_func
        self.__cursor = os.path.getsize(files)
        self.deque = deque(maxlen=3)
        self.number = self.behind = behind
        self.time_format = time_format
        self.auto_cut = auto_cut
        self.file_exists = 0
        self.is_end_of_file = False
        self.send_mail = SendEmail()

    def __read_file(self):
        """
        读取文件内容，并能读取切割后的文件
        """
        try:
            with open(self.__files) as f:
                end_of_file = os.path.getsize(self.__files)
                if end_of_file < self.__cursor and self.auto_cut:
                    with open(self.cut()) as f_prev:
                        f_prev.seek(self.__cursor)
                        yield from f_prev
                f.seek(self.__cursor)
                yield from f
                self.__cursor = f.tell()
                self.file_exists = 0
        except FileNotFoundError:
            self.file_exists += 1
            if self.file_exists > 3:
                print("File is NotFound")

    def main_parse(self):
        """
        日志内容处理，检索到
        异常后，会将后续的几
        行都放入deque中一并返回
        """
        for line in self.__read_file():
            if self.number < self.behind:
                self.deque.append(line)
                self.number += 1
                if self.number == self.behind:
                    self.send()
                    print("is_send")
                    self.number = 0
                    return
                continue
            for pattern_t in self.patterns:
                pattern = re.compile(pattern_t)
                m = pattern.search(line.rstrip("\n"))
                if m:
                    self.number = 0
                    self.deque.append(line)

    def cut(self):
        """
        生成前一天的日志切割文件
        路径，以便检索切割前的内容
        """
        yesterday = datetime.today() - timedelta(days=1)
        prev_date = yesterday.strftime(self.time_format)
        pre_file = self.__files + prev_date
        return pre_file

    def send(self):
        """
        执行邮件发送
        """
        dictionary = self.mail_build_func.generate_dict("".join(self.deque))
        self.send_mail.build_mail(**dictionary)
        self.send_mail.send()

