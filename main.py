import os
import pytz
from base.scheduler import Blocking
from pyhocon import ConfigFactory
from func.thanatosis import CheckDead
from var.m_log_var import GenerateMonitorVar
from var.dead_var import GenerateEmailVar
from func.log_momitor import LogMonitor
from m_error.custom_error import *
from middle.argumentParse import arg_parse


class BaseAddConf:
    def __init__(self, conf_name):
        """
        这是一个基类，子类继承时，需要重写 conf_name
        :param params_string: dict，需要读取的项目配置参数，
                             子类可使用self.add_params_string添加额外配置
        :param params: dict，读取配置文件中，各项目的配置
        :param items: list，每个params都附加到items做轮询处理
        """
        self.conf_name = conf_name
        self.conf = self.build_conf(self.conf_name)
        self.params_string = {"project": 0, "recipients": 1, "log_path": 0, "scheduler": 1}
        self.params = {}
        self.items = []

    def inspect_params(self, item):
        """
        检查配置项是否有空值
        :param item: 轮询查看每个item
        """
        for key, value in item.items():
            if value is None:
                raise ParamsIsNone(key, self.conf_name)

    def parse_params(self, key, element, is_global=None):
        """
        生成self.params中的参数
        """
        if is_global:
            global_params = "global." + key
            self.params[key] = element.get(key, self.conf.get(global_params))
            return
        self.params[key] = element.get(key)

    @staticmethod
    def total_seconds(scheduler_time):
        """
        将时间计算成秒数
        """
        count_seconds = 0
        for k, v in scheduler_time.items():
            if k == "hours" or k == "hour":
                count_seconds += 3600 * v
            elif k == "minutes" or k == "minute":
                count_seconds += 60 * v
            elif k == "seconds" or k == "second":
                count_seconds += v
        return count_seconds

    def add_params_string(self, dictionary):
        """
        附加额外的配置参数
        """
        self.params_string.update(dictionary)

    def parse_config(self, add_params_string):
        """
        读取配置文件中的配置项
        """
        self.add_params_string(add_params_string)
        for element in self.conf.get("thread").values():
            for k, v in self.params_string.items():
                self.parse_params(k, element, v)
            self.items.append(self.params)
            self.params = {}

    @staticmethod
    def build_conf(conf):
        """
        读取conf目录下配置文件
        :param conf: 传入配置文件名
        :return: 配置文件解析对象
        """
        conf_dir = "conf/"
        dir_result = ConfigFactory.parse_file(os.path.join(os.getcwd(), conf_dir, conf))
        return dir_result

    def parse_conf(self):
        """
        读取配置文件中的配置项
        """
        pass


class AddDeadConfig(BaseAddConf):
    def __init__(self, conf_name="settings.conf"):
        """
        监控进程假死
        """
        super().__init__(conf_name)

    def __generate(self, process_name):
        """
        生成邮件标题、正文字典的嵌套格式
        :param process_name: 进程名称
        """
        email_dict = GenerateEmailVar(process_name=process_name,
                                      **self.conf.get("global.subj_body"))
        dictionary = email_dict.generate_dict()
        return dictionary

    def add_dead_monitor(self, func):
        """
        :param func: 传入APScheduler的add_job函数，用来添加任务
        """
        add_params_string = {"counts_send": 1}
        self.parse_config(add_params_string)
        for item in self.items:
            self.inspect_params(item)
            delay = self.total_seconds(item["scheduler"])
            check_dead = CheckDead(item["log_path"],
                                   item["counts_send"],
                                   delay,
                                   self.__generate(item["project"]),
                                   item["recipients"])
            func(check_dead.main_check,
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **item["scheduler"])


class AddLogConfig(BaseAddConf):
    def __init__(self, conf_name="settings_log.conf"):
        """
        日志异常信息检索主函数
        """
        super().__init__(conf_name)

    def add_log_monitor(self, func):
        """
        :param func: 传入APScheduler的add_job函数，用来添加任务
        """
        add_params_string = {"counts_send": 1, "patterns": 1, "auto_cut": 1, "subject": 1}
        self.parse_config(add_params_string)
        for item in self.items:
            self.inspect_params(item)
            mail_build_func = GenerateMonitorVar(subject=item["subject"],
                                                 process_name=item["project"],
                                                 recipients=item["recipients"])

            log_monitor = LogMonitor(item["log_path"],
                                     item["patterns"],
                                     mail_build_func,
                                     item["auto_cut"])
            func(log_monitor.main_parse,
                 max_instances=10,
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **item["scheduler"])


def check_arg():
    counts = 0
    rest = arg_parse()
    if rest.dead:
        parse_config = AddDeadConfig()
        parse_config.add_dead_monitor(scheduler.add_job)
        counts += 1
    if rest.log:
        add_log_config = AddLogConfig()
        add_log_config.add_log_monitor(scheduler.add_job)
        counts += 1
    return counts 


if __name__ == '__main__':
    scheduler = Blocking()
    counts = check_arg()

    if counts > 0:
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
    else:
        arg_parse(["-h"])
