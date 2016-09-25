#!/usr/bin/env python
from flask import Flask,render_template,session,redirect,url_for,flash
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
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Shell
from flask.ext.migrate import Migrate,MigrateCommand
import os

class NameForm(Form):
    name=StringField('what is your name?',validators=[Required()])
    submit=SubmitField('Submit')


basedir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.config['SECRET_KEY']='hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']=\
        'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment=Moment(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)

class Role(db.Model):
    __tablename__='role'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    users=db.relationship('User',backref='role',lazy='dynamic')
    def __repr__(self):
        return '<Role %r>'% self.name

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'))
    def __repr__(self):
        return '<User %r>'% self.username


@app.route('/',methods=['GET','POST'])
def index():
    name=None
    form=NameForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.name.data).first()
        if user is None:
            user =User(username=form.name.data)
            db.session.add(user)
            session['konwn'] = False
        else:
            session['known'] = True
        session['name']= form.name.data
        form.name.data=''
        return redirect(url_for('index'))
    return render_template('index.html',form=form,name=session.get('name'),
            known=session.get('known',False))

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)



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
    manager.add_command("shell",Shell(make_context=make_shell_context))
    manager.run()
