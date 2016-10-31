from flask_mail import Message
from app import mail
from flask import render_template
class MyMessage(Message):
    def __init__(self,subject,sender,recipients):
        super(MyMessage,self).__init__(subject,sender=sender,recipients=recipients)
        body='text body'

msg=MyMessage('mysubject','879651072@qq.com',['879651072@qq.com'])
msg.body='text body'
msg.html='<b>HTML</b> body'




def send_email(to,subject,template,**kwargs):
    msg=Message("*TecnologyDreamer*"+subject,sender='879651072@qq.com',recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    mail.send
