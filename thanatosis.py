import os
import time
from datetime import datetime, timedelta
from sendmail import SendEmail


class CheckDead:
    def __init__(self, delta=15):
        self.delta = delta
        self.previous_time = None
        self.previous_size = None
        self.first = False

    def __is_first(self, logfile):
        if not self.first:
            self.previous_size = os.path.getsize(logfile)
            self.previous_time = datetime.now()
            self.first = True
            time.sleep(5)

    def check(self, logfile):
        self.__is_first(logfile)
        size = os.path.getsize(logfile)
        now = datetime.now()
        if size == self.previous_size:
            delta = now - self.previous_time
            if delta > timedelta(seconds=self.delta):
                print(4444)  ####
        else:
            self.previous_time = now
            self.previous_size = size


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
