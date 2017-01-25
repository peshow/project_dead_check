import os
import pytz
from base.scheduler import Blocking
from pyhocon import ConfigFactory
from func.thanatosis import CheckDead
from conf.email_var import GenerateEmailVar, GenerateMonitorVar
from func.log_momitor import LogMonitor


def build_conf(conf):
    conf_dir = "conf/"
    dir_result = ConfigFactory.parse_file(os.path.join(os.getcwd(), conf_dir, conf))
    return dir_result


class ParseConfig:
    def __init__(self):
        self.__conf = build_conf("settings.conf")

    def __generate(self, process_name):
        email_dict = GenerateEmailVar(process_name=process_name, **{k: v for k, v in self.__conf.get("subj_body").items()})
        dictionary = email_dict.generate_dict()
        return dictionary

    def dead_conf(self, func):
        for key, element in self.__conf.get("thread").items():
            project = element.get("project")
            recipients = element.get("recipients")
            counts_send = element.get("counts_send")
            log_path = element.get("log_path")
            check_dead = CheckDead(self.__generate(project), recipients)

            dictionary = {k: v for k, v in element.get("scheduler").items()}
            func(check_dead.check,
                 args=[log_path, counts_send],
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **dictionary)


class AddLogConfig:
    def __init__(self):
        self.__conf = build_conf("log_settings.conf")

    def __generate(self, process_name, recipients):
        return GenerateMonitorVar(self.__conf.get("subj_body.subject"),
                                  process_name=process_name,
                                  recipients=recipients)

    def add_log_monitor(self, func):
        for key, element in self.__conf.get("thread").items():
            project = element.get("project")
            recipients = element.get("recipients")
            log_path = element.get("log_path")
            patterns = element.get("patterns")
            auto_cut = element.get("auto_cut")

            log_monitor = LogMonitor(log_path, patterns, self.__generate(project, recipients), auto_cut)
            dictionary = {k: v for k, v in element.get("scheduler").items()}
            func(log_monitor.parse_and_send,
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **dictionary)


if __name__ == '__main__':
    scheduler = Blocking()

    # parse_config = ParseConfig()
    # parse_config.dead_conf(scheduler.add_job)

    add_log_config = AddLogConfig()
    add_log_config.add_log_monitor(scheduler.add_job)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
