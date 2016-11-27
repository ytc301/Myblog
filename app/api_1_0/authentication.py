from flask_httpauth import HTTPBasicAuth
from . import User
from .errors import forbidden

auth=HTTPBasicAuth()

@auth.vertify_password
def vertify_password(email,password):
    if email=='':
        g.current_user=AnonymousUser()
        return True
    user=User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user=user
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.route('/posts/')
@auth.login_required
def get_posts():
    pass

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user is_anonymous and \
            not g.current_user.confirm:
        return forbidden('UNconfirmed account')
