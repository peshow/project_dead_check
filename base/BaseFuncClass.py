import os
from m_error.custom_error import *
from pyhocon import ConfigFactory
from var.global_var import BASE_DIR


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
        self.conf = ConfigFactory.parse_file(os.path.join(BASE_DIR, "conf/", self.conf_name))
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
        dictionary:
        0 - not global parameter
        1 - global parameter
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

    def parse_conf(self):
        """
        读取配置文件中的配置项
        """
        pass