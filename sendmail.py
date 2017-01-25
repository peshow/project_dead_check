from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from pyhocon import ConfigFactory
import smtplib
import os


class SendEmail:
    def __init__(self):
        self.__conf = ConfigFactory.parse_file(os.path.join(os.getcwd(), 'conf/mail.conf')).get("email")

        self.smtp_server = self.__conf.get("smtp")
        self.port = self.__conf.get("port")
        self.user = self.src = self.__conf.get("src")
        self.password = self.__conf.get("password")
        self.recipients_list = None
        self.msg = None

    def _format_address(self, s):
        name, address = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), address))

    def build_mail(self, mail_body, subject=None, recipients=None):
        recipients = recipients or self.__conf.get("email.recipients")
        self.recipients_list = recipients.split(",")

        self.msg = MIMEText(mail_body, "html", 'utf-8')
        self.msg['To'] = self._format_address("Recipient <{}>".format(recipients))
        self.msg['From'] = self._format_address("m1world.com <{}>".format(self.src))
        self.msg['Subject'] = Header(subject, 'utf-8')

    def send(self):
        server = smtplib.SMTP(self.smtp_server, self.port)                  # connect smtp server
        server.login(self.user, self.password)                              # login
        server.sendmail(self.src, self.recipients_list, self.msg.as_string())    # send email content
        server.quit()

