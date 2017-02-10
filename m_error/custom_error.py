

class ParamsIsNone(Exception):
    def __init__(self, param, conf):
        self.param = param
        self.conf = conf

    def __str__(self):
        return "{conf} argument: {param} can't is empty!"\
            .format(conf=self.conf, param=self.param)


class EmailParamNotSet(Exception):
    def __init__(self, param):
        self.param = param

    def __str__(self):
        return "conf/mail.conf {} parameter not setting".format(self.param)