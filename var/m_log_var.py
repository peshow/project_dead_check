from .global_var import *


class GenerateMonitorVar(GetTimeMixIn):
    def __init__(self, subject=None, process_name=None, recipients=None):
        """
        生成日志异常信息监控的'标题,正文,收件人列表'
        :param subject: 邮件发送的标题
        :param process_name: 处理的进程名称
        :param recipients: 邮件发送人列表，必须是以逗号分隔的string
        """
        self.subject= subject
        self.process_name = process_name
        self.recipients = recipients

    def edit_subject(self):
        return self.subject.format(self.process_name)

    def generate_mail_body(self, body):
        """
        日志异常信息的正文需要接收
        检索到的异常信息，因此将该
        函数传递到log_monitor， 接
        收body参数
        """
        mail_body = '''
        <p><strong>IP:</strong> {ip}</p>
        <p><strong>Date:</strong> {date}<p>
        <p><strong>Project:</strong> {process_name}<p>
        <strong>Content:</strong>
        <pre>{body}</pre>'''.format(ip=IP,
                                    date=self.get_current_time(),
                                    process_name=self.process_name,
                                    body=body)
        return mail_body

    def generate_dict(self, body):
        """
        :param body: 传递检索到的错误信息生成邮件正文
        :return: 返回邮件发送所需的标题、正文、收件人列表
        """
        dictionary = {
            "subject": self.edit_subject(),
            "mail_body": self.generate_mail_body(body),
            "recipients": self.recipients
        }
        return dictionary
