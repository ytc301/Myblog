from flask_httpauth import HTTPBasicAuth
from . import User
from .errors import forbidden

auth=HTTPBasicAuth()

@auth.vertify_password
def vertify_password(email,password):
    if email=='':
        g.current_user=AnonymousUser()
        return True
    if password=='':
        g.current_user=User.vertify_auth_token(email_or_token)
        g.token_used=True
        return g.current_user is not None
    user=User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user=user
    g.token_used=False
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

@api.route('/token')
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600),'expiration':3600})
