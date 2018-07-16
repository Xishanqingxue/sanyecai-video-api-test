# -*- coding:utf-8 -*-
from base.base_log import BaseLogger
import datetime
import json
import redis
import settings

logger = BaseLogger(__name__).get_logger()


class BaseRedis(object):
    redis_host = settings.REDIS_CONFIG['host']
    redis_port = settings.REDIS_CONFIG['port']
    redis_db = 0


    def __init__(self):
        self.r = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        logger.info('Redis connection is successful...')
        logger.info('host:{0} port:{1} db:{2}'.format(self.redis_host,self.redis_port,self.redis_db))

    def set(self, key, value):
        logger.info('set {0} {1}'.format(key,value))
        return self.r.set(key, value)

    # 设置 key 对应的值为 string 类型的 value。如果 key 已经存在,返回 0,nx 是 not exist 的意思
    def setnx(self, key, value):
        logger.info('setnx {0} {1}'.format(key,value))
        return self.r.setnx(key, value)

    def hset(self, name, key, content):
        logger.info('hset {0} {1} {2}'.format(name,key,content))
        return self.r.hset(name=name, key=key,value=content)

    def delete(self, key):
        logger.info('delete {0}'.format(key))
        return self.r.delete(key)

    def hdel(self, name, key=None):
        if (key):
            logger.info('hdel {0} {1}'.format(name,key))
            return self.r.hdel(name, key)
        logger.info('hdel {0}'.format(name))
        return self.r.hdel(name)

    def hget(self,name,key):
        logger.info('hget {0} {1}'.format(name,key))
        return self.r.hget(name,key)

    def get(self,name):
        logger.info('get {0}'.format(name))
        return self.r.get(name)

    def srem(self,name,value):
        logger.info('srem {0} {1}'.format(name,value))
        return self.r.srem(name,value)

    def zadd(self,name,args,kwargs):
        logger.info('zadd {0} {1} {2}'.format(name,args,kwargs))
        self.r.zadd(name,args,kwargs)

