from flask import render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required
from . import auth
from .forms import LoginForm,RegistrationForm
from ..models import User
from app import db

@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remeber_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invaild user name or password')
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
        flash('You can now login')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)
