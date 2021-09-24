
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature


def generate_auth_token(user_id, expiration=36000):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({
        'user': user_id
    }).decode()


def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        return data
    except SignatureExpired as se:
        print(se)
        return None
    except BadSignature as be:
        print(be)
        return None


