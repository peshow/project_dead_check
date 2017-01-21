import os
import pytz
from base.scheduler import Blocking
from pyhocon import ConfigFactory
from thanatosis import CheckDead
from conf.email_var import GenerateEmailVar


class ParseConfig:
    def __init__(self):
        self.__conf = ConfigFactory.parse_file(os.path.join(os.getcwd(), "conf/settings.conf"))
        self.__Email_dict = GenerateEmailVar()

    def __generate(self, process_name):
        email_dict = self.__Email_dict.generate_dict(process_name)
        return email_dict

    def add_conf(self, func):
        for key, element in self.__conf.get("thread").items():
            dictionary = dict()
            project = element.get("project")
            recipients = element.get("recipients")
            counts_send = element.get("counts_send")
            logfile = element.get("log_path")
            check_dead = CheckDead(self.__generate(project), recipients)

            for k, v in element.get("scheduler").items():
                dictionary[k] = v
            func(check_dead.check,
                 args=[logfile, counts_send],
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **dictionary)


if __name__ == '__main__':
    scheduler = Blocking()

    parse_config = ParseConfig()
    parse_config.add_conf(scheduler.add_job)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()