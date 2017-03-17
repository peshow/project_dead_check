import os
import pytz
from base.scheduler import Blocking
from pyhocon import ConfigFactory
from func.thanatosis import CheckDead
from var.m_log_var import GenerateMonitorVar
from var.dead_var import GenerateEmailVar, GeneralMailMixIn
from func.log_momitor import LogMonitor
from func.inspect_process_alive import InspectProcessAlive
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
        CONVERT = {
            "hours": 3600,
            "hour": 3600,
            "minutes": 60,
            "minute": 60,
            "second": 1,
            "seconds": 1,
        }
        count_seconds = 0
        for k, v in scheduler_time.items():
            if k != "trigger":
                count_seconds += v * CONVERT[k]
        return count_seconds

    def add_params_string(self, dictionary=None):
        """
        附加额外的配置参数
        """
        if dictionary:
            self.params_string.update(dictionary)

    def del_params_string(self, *args):
        first, *_ = args
        if first is not None:
            for key in args:
                self.params_string.pop(key)

    def edit_params_string(self, add=None, delete=None):
        """
        overwrite this function, general the params
        """
        self.add_params_string(add)
        self.del_params_string(delete)
        self.parse_config()

    def parse_config(self):
        """
        读取配置文件中的配置项
        """
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


class AddDeadConfig(BaseAddConf, GeneralMailMixIn):
    def __init__(self, conf_name="settings.conf"):
        """
        监控进程假死
        """
        super().__init__(conf_name)

    def add_dead_monitor(self, func):
        """
        :param func: 传入APScheduler的add_job函数，用来添加任务
        """
        add = {"counts_send": 1, "command": 0}
        self.edit_params_string(add)
        for item in self.items:
            self.inspect_params(item)
            delay = self.total_seconds(item["scheduler"])
            check_dead = CheckDead(item["project"],
                                   item["log_path"],
                                   item["counts_send"],
                                   item["command"],
                                   self.generate(item["project"]),
                                   item["recipients"],
                                   delay)
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
        add = {"counts_send": 1, "patterns": 1, "auto_cut": 1, "subject": 1, "behind": 1, "format": 1}
        self.edit_params_string(add)
        for item in self.items:
            self.inspect_params(item)
            mail_build_func = GenerateMonitorVar(subject=item["subject"],
                                                 process_name=item["project"],
                                                 recipients=item["recipients"])

            log_monitor = LogMonitor(item["log_path"],
                                     item["patterns"],
                                     mail_build_func,
                                     item["auto_cut"],
                                     item["format"])
            func(log_monitor.main_parse,
                 max_instances=10,
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **item["scheduler"])


class AddAliveConfig(GeneralMailMixIn, BaseAddConf):
    def __init__(self, conf_name="settings_alive.conf"):
        super().__init__(conf_name)

    def add_process_alive(self, func):
        add = {"command": 0}
        delete = ["log_path"]
        self.edit_params_string(add, *delete)
        for item in self.items:
            self.inspect_params(item)
            inspect_process_alive = InspectProcessAlive(item["project"],
                                                        item["command"],
                                                        self.generate(item["project"]),
                                                        item["recipients"])
            func(inspect_process_alive.main_inspect,
                 max_instances=10,
                 timezone=pytz.timezone("Asia/Shanghai"),
                 **item["scheduler"])


def check_arg(scheduler):
    counts = 0
    rest = arg_parse()
    if rest.dead:
        parse_config = AddDeadConfig()
        parse_config.add_dead_monitor(scheduler.add_job)
        counts += 1
    if rest.logging:
        add_log_config = AddLogConfig()
        add_log_config.add_log_monitor(scheduler.add_job)
        counts += 1
    if rest.alive:
        parse_config = AddAliveConfig()
        parse_config.add_process_alive(scheduler.add_job)
        counts += 1
    return counts 


if __name__ == '__main__':
    scheduler = Blocking()
    counts = check_arg(scheduler)

    if counts > 0:
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
    else:
        arg_parse(["-h"])
