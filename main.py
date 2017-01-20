import os
import pytz
from functools import wraps
from base.scheduler import Blocking
from pyhocon import ConfigFactory
from thanatosis import CheckDead


class ParseConfig:
    def __init__(self):
        self.__conf = ConfigFactory.parse_file(os.path.join(os.getcwd(), "conf/settings.conf"))
        self.__dict = dict()

    def add_conf(self, func):
        @wraps(func)
        def wrapper():
            for element in self.__conf.get("thread").values():
                check_dead = CheckDead()
                logfile = element.get("log_path")
                for k, v in element.get("scheduler").items():
                    self.__dict[k] = v
                func(check_dead.check, args=[logfile], **self.__dict)
        return wrapper


if __name__ == '__main__':
    scheduler = Blocking()

    parse_config = ParseConfig()
    parse_config.add_conf(scheduler.add_job)()
    try:
        print(scheduler.scheduler.get_jobs())
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()