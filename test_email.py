# coding:utf-8

import smtplib
from email.mime.text import MIMEText

email_str = 'testtest'
title = 'doubi'
msg = MIMEText(email_str.encode('utf-8'), 'html', 'utf-8')
msg['Subject'] = title.encode('utf-8')
msg['From'] = 'zuoyuan@mail.ustc.edu.cn'
msg['To'] = '563876960@qq.com'

s = smtplib.SMTP('smtp.163.com')
s.login('tracholar_devtest@163.com',open('email163pw.txt').read())
s.sendmail('xxx@mail.ustc.edu.cn', ['wenshixue@qq.com'], msg.as_string())
s.quit()