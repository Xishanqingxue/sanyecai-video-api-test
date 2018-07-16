# -*- coding:utf-8 -*-
from base.base_runner import BaseRunner
from base.base_email import BaseMail


if __name__ == '__main__':
    """
    1、运行全部测试用例
    2、生成测试报告
    3、自动发送邮件
    """
    BaseRunner().run_tests()
    BaseMail().send_mail()