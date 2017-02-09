import os
import pytz
from base.scheduler import Blocking
from pyhocon import ConfigFactory
from func.thanatosis import CheckDead
from conf.email_var import GenerateEmailVar, GenerateMonitorVar
from func.log_momitor import LogMonitor
from m_error.custom_error import ParamsIsNone


def build_conf(conf):
    """
    读取conf目录下配置文件
    :param conf: 传入配置文件名
    :return: 配置文件解析对象
    """
    conf_dir = "conf/"
    dir_result = ConfigFactory.parse_file(os.path.join(os.getcwd(), conf_dir, conf))
    return dir_result


class AddDeadConfig:
    def __init__(self):
        """

        """
        self.__conf = build_conf("settings.conf")

    def __generate(self, process_name):
        email_dict = GenerateEmailVar(process_name=process_name, **{k: v for k, v in self.__conf.get("global").items()})
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
    def __init__(self, conf_name="settings_log.conf"):
        """
        日志异常信息检索主函数
        """
        self.conf_name = conf_name
        self.__conf = build_conf(conf_name)
        self.__params = {}
        self.__items = []
    
    def __inspect_params(self, item):
        """
        检查配置项是否有空值
        :param item: 轮询查看每个item
        """
        for key, value in item.items():
            if value is None:
                raise ParamsIsNone(key, self.conf_name)
            
    def __parse_config(self):
        """
        读取配置文件中的配置项
        """
        for key, element in self.__conf.get("thread").items():
            self.__params["project"] = element.get("project")
            self.__params["recipients"] = element.get("recipients", self.__conf.get("global.recipients"))
            self.__params["log_path"] = element.get("log_path")
            self.__params["patterns"] = element.get("patterns", self.__conf.get("global.patterns"))
            self.__params["auto_cut"] = element.get("auto_cut", self.__conf.get("global.auto_cut"))
            self.__params["subject"] = element.get("subject", self.__conf.get("global.subject"))
            self.__params["scheduler"] = element.get("scheduler", self.__conf.get("global.scheduler"))

            self.__items.append(self.__params)
            self.__params = {}

    def add_log_monitor(self, func):
        """
        :param func: 传入APScheduler的add_job函数，用来添加任务
        """
        self.__parse_config()
        for item in self.__items:
            self.__inspect_params(item)
            mail_build_func = GenerateMonitorVar(subject=item["subject"],
                                                 process_name=item["project"],
                                                 recipients=item["recipients"])

            log_monitor = LogMonitor(item["log_path"],
                                     item["patterns"],
                                     mail_build_func,
                                     item["auto_cut"])
            func(log_monitor.main_parse,
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **item["scheduler"])


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
