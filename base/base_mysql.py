# -*- coding:utf-8 -*-
import pymysql.cursors
import settings
from base.base_log import BaseLogger


logger = BaseLogger(__name__).get_logger()

def execute(sql, params=None, db=settings.TEST_MYSQL_CONFIG['db'], is_fetchone=True):
    # Connect to the database
    connection = pymysql.connect(host=settings.TEST_MYSQL_CONFIG['host'],
                                 port=settings.TEST_MYSQL_CONFIG['port'],
                                 user=settings.TEST_MYSQL_CONFIG['user'],
                                 password=settings.TEST_MYSQL_CONFIG['password'],
                                 db=db,
                                 autocommit=True,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    logger.info('Executing SQL：' + str(sql) + ',params:' + str(params))
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            if is_fetchone:
                return cursor.fetchone()
            else:
                return cursor.fetchall()
    except:
        connection.rollback()
    finally:
        connection.close()


def local_execute(sql, params=None, db='auto_test', is_fetchone=True):
    # 链接测试报告库
    connection = pymysql.connect(host=settings.TEST_MYSQL_CONFIG['host'],
                                 port=settings.TEST_MYSQL_CONFIG['port'],
                                 user=settings.TEST_MYSQL_CONFIG['user'],
                                 password=settings.TEST_MYSQL_CONFIG['password'],
                                 db=db,
                                 autocommit=True,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    logger.info('Executing SQL：' + str(sql) + ',params:' + str(params))
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            if is_fetchone:
                return cursor.fetchone()
            else:
                return cursor.fetchall()
    except:
        connection.rollback()
    finally:
        connection.close()