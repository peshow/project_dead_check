import sys
import argparse


def arg_parse(arg=sys.argv[1:]):
    parse = argparse.ArgumentParser(description="自定义监控")
    parse.add_argument("-d", dest="dead", action="store_true", default=False, help=":启动进程假死监控")
    parse.add_argument("-m", dest="logging", action="store_true", default=False, help=":启动日志异常检索")
    parse.add_argument("-i", dest="alive", action="store_true", default=False, help=":启动进程存活监控")
    rest = parse.parse_args(arg)
    return rest
