import argparse
import sys


def arg_parse():
    parse = argparse.ArgumentParser(description="Error Monitor")
    parse.add_argument("-d", dest="dead", action="store_true", default=False, help=":启动假死监控")
    parse.add_argument("-l", dest="log", action="store_true", default=False, help=":启动日志异常检索")
    rest = parse.parse_args(sys.argv[1:])
    return rest

if __name__ == '__main__':
    a = arg_parse()
    if a.dead:
        print(1234)
    if a.log:
        print(7777)
