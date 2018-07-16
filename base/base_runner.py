# -*- coding:utf-8 -*-
import HTMLTestRunner
import unittest
import os
import settings
from base.base_log import BaseLogger


logger = BaseLogger(__name__).get_logger()


class BaseRunner(object):

    def __init__(self,test_dir_path='./test_case'):
        self.test_dir_path = os.path.abspath(test_dir_path)

    def create_suite(self):
        """
        创建测试套件，并且将用例添加到测试套件
        :return:
        """
        test_unit = unittest.TestSuite()
        discover = unittest.defaultTestLoader.discover(start_dir=self.test_dir_path, pattern='test*.py')
        logger.info('Create test suite success.')
        for test_suite in discover:
            for test_case in test_suite:
                test_unit.addTest(test_case)
        logger.info('Use cases are added to the test suite for completion.')
        logger.info('All use cases are added in the following order.')
        logger.info('##### ##### ' * 7)
        # for case in test_unit._tests:
        #     logger.info('{0}:{1}'.format(self.counter,case._testMethodName))
        #     self.counter+=1
        logger.info('##### ##### ' * 7)
        return test_unit

    def run_tests(self):
        """
        运行测试用例并生成测试报告
        :return:
        """
        logger.info('Initializing the test report.')
        fp = open(settings.REPORT_FILE_NAME,'wb+')
        title = settings.REPORT_TITLE
        description = settings.REPORT_DESCRIPTION
        tester = settings.REPORT_TESTER
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=title, description=description, tester=tester, verbosity=2)
        logger.info('The testing process is about to begin.')
        runner.run(self.create_suite())
        logger.info('End of the test.')
        fp.close()
        logger.info('The test report is written to completion.')