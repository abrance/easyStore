use store;

# 用户信息表
create table user(
    user_id int auto_increment primary key NOT NULL,
    username VARCHAR(32) NOT NULL,
    email VARCHAR(32) ,
    phone CHAR(11) ,
    password CHAR(32) NOT NULL ,
    is_delete TINYINT NOT NULL ,
    create_time DATETIME NOT NULL
);

# pool 存储池， type 挂载方式 net local 等
# 存储池信息表
create table pool(
    pool_id int auto_increment primary key NOT NULL ,
    pool VARCHAR(32) UNIQUE NOT NULL ,
    type VARCHAR(32) NOT NULL ,
    area VARCHAR(64) NOT NULL ,
    create_time DATETIME NOT NULL
);

# space 以M为单位，单个文件不足1M按1M算，因为不建议存小文件 最大2147483647M
# 每个用户拥有的存储池表
create table user_pool(
    up_id int auto_increment primary key NOT NULL ,
    user_id int NOT NULL ,
    pool_id int NOT NULL ,
    space int NOT NULL ,
    create_time DATETIME NOT NULL
);

# 文件源信息表
create table file(
    fileid int auto_increment primary key NOT NULL ,
    file VARCHAR(255) NOT NULL ,
    size int NOT NULL ,
    parent_id int ,
    user_id int not null ,
    create_time DATETIME NOT NULL
);