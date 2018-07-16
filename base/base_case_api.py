# -*- coding:utf-8 -*-
from unittest import TestCase
from base.base_log import BaseLogger

logging = BaseLogger(__name__).get_logger()


class BaseCase(TestCase):

    pass
