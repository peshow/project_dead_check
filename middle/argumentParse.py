import sys
import argparse 

def arg_parse(arg=sys.argv[1:]):
    parse = argparse.ArgumentParser(description="自定义监控")
    parse.add_argument("-d", dest="dead", action="store_true", default=False, help=":启动进程假死监控")
    parse.add_argument("-l", dest="log", action="store_true", default=False, help=":启动日志异常检索")
    rest = parse.parse_args(arg)
    return rest
