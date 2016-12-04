#!/usr/bin/env python
#coding:utf-8

import os
from app import create_app,db
from app.models import User,Role,Post
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

COV=None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV=coverage.coverage(branch=True,include='app/*')
    COV.start()

#FLASKY_CONFIG是环境变量,根据环境变量的获取不同的配置,
#默认是获取开发配置
app=create_app(os.getenv('FLASK_CONFIG') or 'default')

manager=Manager(app)
"""
创建manage对象,该对象以flask的程序app为参数创建,后续进行
app的管理,使启动服务器时支持命令行.
Example:
    开启服务器:python manage.py runserver
"""

migrate=Migrate(app,db)
"""
创建migrate对象,用来管理数据库的迁移等相关工作,Migrate接受两个参数
"""

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Post=Post)

manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

@manager.command
def test():
    """运行单元测试"""
    import unittest
    tests=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def myprint():
    print 'hello world'

@manager.command
def test(coverage=False):
    """Run The Unit Test"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE']='1'
        os.execvp(sys.executable,[sys.executable]+sys.argv)
    import unittest
    test=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(test)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary')
        COV.report()
        basedir=os.path.abspath(os.path.dirname(__file__))
        covdir=os.path.join(basedir,'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version:file://%s/index.html'%covdir)
        COV.erase()

@manager.command
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade
    from app.models import Role,User

    upgrade()

    Role.insert_roles()

    User.add_self_follows()

if __name__=='__main__':
    manager.run()
