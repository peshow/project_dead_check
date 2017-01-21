from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from pyhocon import ConfigFactory
import smtplib
import os


class SendEmail:
    def __init__(self):
        self.__conf = ConfigFactory.parse_file(os.path.join(os.getcwd(), 'conf/settings.conf'))

    def _format_address(self, s):
        name, address = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), address))

    def send_mail(self, mail_body, subject=None, recipients=None):
        smtp_server = self.__conf.get("email.smtp")
        src = self.__conf.get("email.src")
        subject = subject or self.__conf.get("email.subject")
        port = self.__conf.get("email.port")
        user = src
        password = self.__conf.get("email.password")
        recipients = recipients or self.__conf.get("email.recipients")
        recipients_list = recipients.split(",")

        msg = MIMEText(mail_body, "plain", 'utf-8')
        msg['To'] = self._format_address("Recipient <{}>".format(recipients))
        msg['From'] = self._format_address("m1world.com <{}>".format(src))
        msg['Subject'] = Header(subject, 'utf-8')

        server = smtplib.SMTP(smtp_server, port)                  # connect smtp server
        server.login(user, password)                              # login
        server.sendmail(src, recipients_list, msg.as_string())    # send email content
        server.quit()

