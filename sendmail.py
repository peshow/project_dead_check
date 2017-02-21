import os
import smtplib
from email.header import Header
from pyhocon import ConfigFactory
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from m_error.custom_error import EmailParamNotSet


class SendEmail:
    ITEMS = {}

    def __init__(self):
        self.__conf = ConfigFactory.parse_file(os.path.join(os.getcwd(), 'conf/mail.conf')).get("email")

        self.params = ["smtp", "port", "src", "password", "user", "send_id"]
        for item in self.params:
            self.general_parm(item)
        self.recipients_list = None
        self.msg = None

    def general_parm(self, param_name):
        if param_name == "user":
            self.ITEMS[param_name] = self.__conf.get("src")
            return
        self.ITEMS[param_name] = self.__conf.get(param_name)

    @staticmethod
    def _format_address(s):
        name, address = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), address))

    def build_mail(self, mail_body, subject=None, recipients=None):
        """
        邮件发送前的准备(The preparation for mail delivery)
        :param mail_body: 传递邮件正文,
        :param subject: 传递邮件标题,
        :param recipients: 传递收件人,必须是以逗号分隔的string,
        """
        recipients = recipients or self.__conf.get("email.recipients")
        self.recipients_list = recipients.split(",")

        self.msg = MIMEText(mail_body, "html", 'utf-8')
        self.msg['To'] = self._format_address("Recipient <{}>".format(recipients))
        self.msg['From'] = self._format_address("{} <{}>".format(self.ITEMS["send_id"], self.ITEMS["src"]))
        self.msg['Subject'] = Header(subject, 'utf-8')

    def check_param(self):
        for key, value in self.ITEMS.items():
            if not value:
                raise EmailParamNotSet(key)

    def send(self):
        """
        执行邮件发送(Perform the mail delivery)
        """
        self.check_param()
        server = smtplib.SMTP(self.ITEMS["smtp"], self.ITEMS["port"])                      # connect smtp server
        server.login(self.ITEMS["user"], self.ITEMS["password"])                                  # login
        server.sendmail(self.ITEMS["src"], self.recipients_list, self.msg.as_string())   # send email content
        server.quit()

