#! -*-coding:utf-8-*-

from app import db,log
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class Permission:
    FOLLOW=0x01
    COMMIT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    defult = db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)
    users=db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>'% self.name
    
    @staticmethod
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW|
                    Permission.COMMIT|
                    Permission.WRITE_ARTICLES,True),

            'Moderator':(
                    Permission.FOLLOW|
                    Permission.COMMIT|
                    Permission.WRITE_ARTICLES|
                    Permission.MODERATE_COMMENTS,False),

            'Administrator':(0xff,False),
            }

        for r in roles:
            role =Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()

class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed=db.Column(db.Boolean,default=False)
    
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email==current_app.config['FLASKY_ADMIN']:
                self.role=Role.query.filter_by(permissions=0xff).first()
            else:
                self.role=Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>'% self.username

    #修饰器，把方法做成属性
    @property
    def password(self):
        raise AttributeError('passwoed is not a readable attribute')
    
    #设置属性的写
    @password.setter
    def password(self,password): 
	self.password_hash=generate_password_hash(password)

    #比较用户输入的密码和保存的密码
    def verify_password(self,password):
	return check_password_hash(self.password_hash,password)

    #生成令牌
    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        token = s.dumps({'confirm':self.id})
        log.write('self.id=',self.id)
        log.write('source token=',token)
        return token

    #确认令牌正确性
    def confirm(self,token):
        log.write('dest token=',token)
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
            log.write('data =',data)
        except:
            return False
        log.write('self.id=',self.id)
        if data.get('confirm')!=self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

