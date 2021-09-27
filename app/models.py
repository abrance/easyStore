import sqlalchemy
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
# 这样写不会标黄
from sqlalchemy.ext.declarative import declarative_base

import contextlib
from datetime import datetime

from app import config
from app.log import logger

Base = declarative_base()


class CommitException(Exception):
    pass


class DuplicateKeyException(Exception):
    pass


# 用户信息表
class User(Base):
    __tablename__ = 'user'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String(32), nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String(32), nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String(11), nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String(32), nullable=False)
    is_delete = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.now())


# pool 存储池， type 挂载方式 net local 等
# 存储池信息表
class Pool(Base):
    __tablename__ = 'pool'
    pool_id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False)
    pool = sqlalchemy.Column(sqlalchemy.String(32), unique=True, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String(32), nullable=False)
    area = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.now())


# space 以M为单位，单个文件不足1M按1M算，因为不建议存小文件
# 每个用户拥有的存储池表
class UserPool(Base):
    __tablename__ = 'user_pool'
    up_id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    pool_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    space = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.now())


# size 如果是目录，标记为-1
# 目录也有fileid，根目录为负数
class File(Base):
    __tablename__ = 'file'
    fileid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    parent_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    create_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.now())


class Database(object):
    def __init__(self):
        self.engine = sqlalchemy.create_engine(
            config.Config.db_conn_str,
            echo=True,  # 输出详细的数据库 SQL 语句
            pool_recycle=3600  # 要求取得的连接不超过一个小时
            # 详情请看官方文档的说明
            # http://docs.sqlalchemy.org/en/rel_1_1/core/pooling.html#setting-pool-recycle
        )
        self.Session = sessionmaker(bind=self.engine)

    # 下面函数管理 session 的生命周期，原因详情请看下面给出的官方文档
    # http://docs.sqlalchemy.org/en/rel_1_1/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
    @contextlib.contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error("exception occurs: {}, {}".format(type(e), e))
            if isinstance(e, IntegrityError):
                ecode = e.orig.args[0]
                if ecode == 1062:  # Duplicate key
                    raise DuplicateKeyException
                else:
                    session.rollback()
                    logger.error("> session commit failed 1, rollback")
                    raise CommitException
            else:
                session.rollback()
                logger.error("> session commit failed 2, rollback")
                raise CommitException
        finally:
            session.close()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def destroy_session(self):
        self.engine.dispose()

    def create_pool(self, pool_id, pool, _type, area):
        try:
            with self.session_scope() as session:
                query_p = session.query(Pool).filter(
                    or_(
                        Pool.pool_id == pool_id,
                        Pool.pool == pool
                    )
                )
                row_p = query_p.first()
                if row_p:
                    logger.error('pool_id: {} has existed'.format(pool_id))
                    return False
                else:
                    row_p = Pool(
                        pool_id=pool_id,
                        pool=pool,
                        type=_type,
                        area=area
                    )
                    session.add(row_p)
                    return True

        except DuplicateKeyException as de:
            logger.error(de)
            return False

    def ls_pool(self, pool_id=None):
        with self.session_scope() as session:
            ls = []
            if pool_id is None:
                query_p = session.query(Pool)
                for row_p in query_p.all():
                    ls.append({
                        'pool_id': row_p.pool_id,
                        'pool_name': row_p.pool_name,
                        'type': row_p.type,
                        'area': row_p.area,
                        'create_time': row_p.create_time
                    })
                return ls
            elif isinstance(pool_id, int):
                query_p = session.query(Pool).filter(
                    Pool.pool_id == pool_id
                )
                row_p = query_p.first()
                if row_p:
                    ls.append({
                        'pool_id': row_p.pool_id,
                        'pool_name': row_p.pool_name,
                        'type': row_p.type,
                        'area': row_p.area,
                        'create_time': row_p.create_time
                    })
                return ls
            else:
                return False


db = Database()
