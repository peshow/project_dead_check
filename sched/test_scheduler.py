import os
import pytz
import time
from base.scheduler import BaseScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


class DeadCheck(BaseScheduler):
    def __init__(self):
        super().__init__()

    def scheduling(self, fn, cron):
        sched = BlockingScheduler()
        sched.add_job(fn)


class Tick:
    def __init__(self, txt):
        self.file = txt
        self.previous_time = datetime.now()
        self.previous_size = os.path.getsize(txt)

    def tick(self):
        size = os.path.getsize(self.file)
        if size > self.previous_size:
            self.previous_time = datetime.now()
            self.previous_size = size
            print('Tick! the time is: {} \
              the file size is {}'.format(self.previous_time, size))
        elif size == self.previous_size:
            print("the file is not change")


if __name__ == '__main__':
    t1 = Tick(FILE)
    scheduler = BackgroundScheduler()
    scheduler.add_job(t1.tick, 'cron', hour=15, minute=5)
    scheduler.start()
    try:
        while True:
            time.sleep(2)
            print("sleep!")
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print('Exit the Job!')