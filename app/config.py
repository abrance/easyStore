from pathlib import Path

from flask import Flask
from flask_cors import CORS


class Config(object):
    """
    global config
    """
    DEBUG = False
    #
    # # LOG_LEVEL = "DEBUG"
    # LOG_LEVEL = "INFO"
    #
    # # DB
    # host = "localhost"
    # port = 3306
    # user = 'root'
    # password = 123456
    root_path = Path.cwd()
    static_path = str(root_path/'static')
    print(static_path)
    upload_path = str(root_path/'upload')
    print(upload_path)

    dbn = "mysql"
    mysql_engine = 'pymysql'
    user = 'store'
    password = '123456'
    host = 'localhost'
    port = '3306'
    db = 'store'
    db_conn_str = '{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4'.\
        format(dbn, mysql_engine, user, password, host, port, db)


app = Flask(__name__, static_folder=Config.static_path)
CORS(app, supports_credentials=True)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
# json化后中文 unicode码问题
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'never-guess'
# app.config['UPLOADED_PHOTOS_DEST'] = Config.upload_path
# app.config['UPLOADED_PHOTO_ALLOW'] = IMAGES


if __name__ == '__main__':
    print(Config.root_path)
