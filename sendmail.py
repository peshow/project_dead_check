from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendmail(mail_body, src, recipients_list, password, smtp_server="smtp.163.com"):
    msg = MIMEText(mail_body, "plain", 'utf-8')
    msg['To'] = _format_addr("Recipient <{}>".format(recipients_list))
    msg['From'] = _format_addr("Author <{}>".format(src))
    msg['Subject'] = Header('Error message', 'utf-8')

    server = smtplib.SMTP(smtp_server, 25)
    server.login(src, password)
    print(msg.as_string())
    server.sendmail(src, [recipients_list], msg.as_string())
    server.quit()

