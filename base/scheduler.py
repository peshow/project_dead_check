# -*- coding:utf-8 -*-
#
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


class BaseScheduler:
    def __init__(self):
        self.scheduler = None
    
    def add_job(self, func, **kwargs):
        self.scheduler.add_job(func, **kwargs)

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=5)

    def get_jobs(self):
        return self.scheduler.get_jobs()


class Blocking(BaseScheduler):
    def __init__(self):
        super().__init__()
        self.scheduler = BlockingScheduler()


class Background(BaseScheduler):
    def __init__(self):
        super().__init__()
        self.scheduler = BackgroundScheduler()