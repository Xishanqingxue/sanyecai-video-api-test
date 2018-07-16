# -*- coding:utf-8 -*-
from base_api.image_code_api import ImageCodeApi
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
import unittest
import settings


class TestImageCodeApi(BaseCase):
    """
    图形验证码
    """
    mobile = '13501077762'

    def test_get_image_code_success(self):
        """
        测试获取图形验证码成功
        :return:
        """
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': self.mobile})

        image_code = Redis().get_image_code(self.mobile)
        self.assertEqual(len(image_code), 4)

    @unittest.skip(reason=settings.SKIP_REASON)
    def test_get_image_code_mobile_null(self):
        """
        测试请求接口手机号为None
        :return:
        """
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': None})

        self.assertEqual(image_code_api.get_resp_code(), 200)

    def test_get_image_code_mobile_error(self):
        """
        测试请求接口手机号格式不对可以获取成功
        :return:
        """
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': '99999999999'})

        image_code = Redis().get_image_code('99999999999')
        self.assertEqual(len(image_code), 4)
