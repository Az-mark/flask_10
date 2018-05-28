import redis
import os

class Config(object):
    DEBUG =False
    SQLALCHEMY_DATABASE_URI ='mysql://root:mysql@localhost:3306/xjzx10'
    SQLALCHEMY_TRACK_MODIFICATIONS= True

    #配置redis
    REDIS_HOST ='localhost'
    REDIS_PORT =6379
    REDIS_DB =10

    SECRET_KEY ='github'
    #flask_session 的配置信息
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    SESSION_REDIS =redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)
    PERMANENT_SESSION_LIFETIME =60*60*24*14

    BASE_DIR =os.path.dirname(os.path.abspath(__file__))
    #七牛云配置


class DevelopConfig(Config):
    DEBUG = True