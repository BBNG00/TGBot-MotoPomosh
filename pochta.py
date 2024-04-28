import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = 'mmm hyeta'

from_imail = ('moto_pomosh_bot@mail.ru')
to_imail = ('moto_pomosh_bot@mail.ru')
password = ('svQhPqLRf1nEVAw4NjdT')


def otpravka_pisma(massage):
    msg = MIMEText(massage, 'plain')
    server = smtplib.SMTP('smtp.mail.ru: 25')
    server.starttls()
    server.login(from_imail, password)
    server.sendmail(from_imail, to_imail, msg.as_string())
    server.quit()

first = otpravka_pisma(msg)