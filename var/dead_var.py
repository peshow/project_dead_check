from .global_var import *
from sendmail import SendEmail


class EmailMixIn:
    """
    邮件发送的MixIn, 用于读取conf中定义error_body,error_subject,ok_send,
    实现简单地邮件正文与标题的发送
    """
    current_counts_error_send = 0
    send_mail = SendEmail()
    error_is_send = False

    def set_mail_info(self, error_or_ok):
        """
        设置邮件的发送信息
        """
        mail_body = self.mail_body.generate_dict(DATE())
        self.send_mail.build_mail(mail_body["{}_body".format(error_or_ok)],
                                  mail_body["{}_subject".format(error_or_ok)],
                                  self.recipients)

    def error_send(self):
        """
        发送异常邮件
        """
        if self.current_counts_error_send < self.counts_send:
            self.current_counts_error_send += 1
            self.error_is_send = True
            self.set_mail_info("error")
            self.logging.info("error {} send".format(self.project))
            self.send_mail.send()
            self.logging.error("Dead monitor error email was send")

    def ok_send(self):
        """
        发送返回正常邮件
        """
        if self.error_is_send:
            self.current_counts_error_send = 0
            self.error_is_send = False
            self.set_mail_info("ok")
            self.logging.info("return ok {} send".format(self.project))
            self.send_mail.send()
            self.logging.error("Dead monitor return ok email was send")


class GeneralMailMixIn:
    """
    用来解析conf中的subj_body, 返回一个字典
    """
    def generate(self, process_name):
        """
        生成邮件标题、正文字典的嵌套格式
        :param process_name: 进程名称
        """
        email_dict = GenerateEmailVar(process_name=process_name,
                                      **self.conf.get("global.subj_body"))
        return email_dict


class GenerateEmailVar:
    def __init__(self, process_name, ok_subject=None, ok_body=None, error_subject=None, error_body=None):
        """
        用来设置邮件的内容格式与标题
        """
        self.ok_subject = ok_subject
        self.ok_body = ok_body
        self.error_body = error_body
        self.error_subject = error_subject
        self.process_name = process_name
        self.subj_body = {}

    def generate_subject(self, is_ok=False):
        subject = self.error_subject.format(self.process_name)
        if is_ok:
            subject = self.ok_subject.format(self.process_name)
        return subject

    def generate_mail_body(self, date, is_ok=False):
        body = self.error_body.format(self.process_name)
        if is_ok:
            body = self.ok_body.format(self.process_name)
        mail_body = '''
        <p><strong>IP:</strong> {ip}</p>
        <p><strong>Date:</strong> {date}<p>
        <p><strong>Project:</strong> {process_name}<p>
        <strong>Content:</strong>
        <pre>{body}</pre>'''.format(ip=IP,
                                    date=date,
                                    process_name=self.process_name,
                                    body=body)
        return mail_body

    def generate_dict(self, date):
        dictionary = {
            "error_subject": self.generate_subject(),
            "error_body": self.generate_mail_body(date),
            "ok_subject": self.generate_subject(is_ok=True),
            "ok_body": self.generate_mail_body(date, is_ok=True)
        }
        return dictionary
