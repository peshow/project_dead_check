import pytz
from base.scheduler import Blocking
from base.BaseFuncClass import BaseAddConf
from func.thanatosis import CheckDead
from var.m_log_var import GenerateMonitorVar
from var.dead_var import GenerateEmailVar, GeneralMailMixIn
from func.log_momitor import LogMonitor
from func.inspect_process_alive import InspectProcessAlive
from middle.argumentParse import arg_parse


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
        add = {"counts_send": 1, "command": 0, "executes": 1}
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
                                   item["executes"],
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
