#!/usr/bin/env python
from flask import Flask,render_template
from flask import request
from flask import make_response
from flask import redirect
from flask import abort
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required


class NameForm(Form):
    name=StringField('what is your name?',validators=[Required()])
    submit=SubmitField('Submit')

app=Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'
manager = Manager(app)
bootstrap = Bootstrap(app)
moment=Moment(app)


@app.route('/',methods=['GET','POST'])
def index():
    name=None
    form=NameForm()
    if form.validate_on_submit():
        name= form.name.data
        form.name.data=''
    return render_template('index.html',form=form,name=name)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500


if __name__=='__main__':
    manager.run()
