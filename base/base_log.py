# coding=utf-8
import logging
import os
import settings

class BaseLogger(object):

    def __init__(self,name):
        """
        初始化logger
        :param name:
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)  # Log等级总开关

    def get_logger(self):
        """
        自定义logger
        :return:
        """
        # 定义handler的输出格式
        formatter = logging.Formatter(settings.LOG_FORMATTER)

        # 创建一个handler，用于写入日志文件
        if settings.ENV == 'test':
            logfile = os.path.join(os.getcwd(),settings.LOG_FILE_NAME)
            file_handler = logging.FileHandler(logfile, mode='w')
            file_handler.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # 再创建一个handler，用于输出到控制台
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)  # 输出到console的log等级的开关
            console_handler.setFormatter(formatter)

            # 将logger添加到handler里面
            self.logger.addHandler(console_handler)
        return self.logger