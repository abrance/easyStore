import json
from pathlib import Path
from functools import wraps

from flask import jsonify, request

from app.config import app, Config
from app.utils import verify_auth_token, generate_auth_token


def error(msg, code=400):
    return {'code': code, 'res': '', 'msg': msg}


def res(data):
    return {'code': 200, 'res': data}


def verify_password(user, password):
    if user:
        # db中进行验证
        if user == 'admin@wz.com' and password == "123456":
            print('pass')
            return True
    return False


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", default=None)
        if token:
            data = verify_auth_token(token)
            print('token: {}'.format(data))
            if data:
                return f(*args, **kwargs)
        else:
            return jsonify(error("403"))
    return wrapper


@app.route("/api/hello")
def hello():
    return jsonify(res('hello'))


@app.route("/api/getDirLs")
@login_required
def getDirLs():
    ls = ['1.txt', 'dir1', '']
    return jsonify(res(ls))


@app.route("/api/uploadFileLs", methods=['POST'])
@login_required
def uploadFileLs():
    file = request.files.get('file')
    # 单一的文件对象
    file.save(str(Path(Config.upload_path) / file.filename))
    return jsonify(res('ok'))


@app.route("/api/login", methods=['POST'])
def login():
    info = request.data
    info = json.loads(info)
    print("info {}".format(info))
    username = info.get('username')
    pwd = info.get('password')
    print("{}\n{}".format(username, pwd))
    ret = verify_password(username, pwd)
    if ret:
        token = generate_auth_token(username)
        print("token {}".format(token))
        return jsonify(res(token))
    else:
        return jsonify(error("auth error"))
