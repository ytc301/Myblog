#!_*_ coding:utf-8 _*_
from flask import render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from . import auth
from .forms import LoginForm,RegistrationForm
from ..models import User
from app import db
from ..email import send_email


@auth.route('/login',methods=['GET','POST'])
def login():
    """
    登录控制,向服务器发送登录的表单.
    """
    #声明登录表单
    form=LoginForm()
    #POST表单时,如果点击了提交按钮,会触发validate_on_submit()事件,该接口
    #定义在登录表单的基类FlaskForm中
    if form.validate_on_submit():
        #根据email从数据库查询并生成user实例
        user = User.query.filter_by(email=form.email.data).first()
        #验证用户填写的密码和user中的hash值是否符合.
        if user is not None and user.verify_password(form.password.data):
            #通过flask_login来管理登录的用户,login_user为其一个接口,用来登录
            #用户,第二个参数是一个布尔量,为True的话记住当前用户存到cookies中
            #重启浏览器后不用再重复输入用户名
            login_user(user,form.remeber_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误!')
    #使用GET时,获取表单,渲染login.html,传入声明的登录表单对象
    return render_template('auth/login.html',form=form);

@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        #生成令牌
        token=user.generate_confirmation_token()
        send_email(user.email,'Confirm your account','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5]!='auth.':
                    return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html',name=current_user.username)

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))
