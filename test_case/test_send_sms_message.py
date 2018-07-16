# -*- coding:utf-8 -*-
from base_api.send_message_api import SendMessageApi
from base_api.image_code_api import ImageCodeApi
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
import settings
import random
import unittest


class TestSendSmsMessageApi(BaseCase):
    """
    发送手机验证码
    """

    def test_send_rz_sms_code(self):
        """
        发送实名认证短信验证码
        :return:
        """
        mobile = '1350101' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

    def test_send_tx_sms_code(self):
        """
        发送提现短信验证码
        :return:
        """
        mobile = '1350102' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'tx_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='tx')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

    def test_send_tj_sms_code(self):
        """
        发送绑定银行卡短信验证码
        :return:
        """
        mobile = '1350103' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'tj_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='tj')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

    def test_send_xg_sms_code(self):
        """
        发送修改手机号/绑定手机号短信验证码
        :return:
        """
        mobile = '1350124' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='xg')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

    def test_send_xg_sms_code_image_code_upper(self):
        """
        测试图形验证码大写情况下短信发送成功
        :return:
        """
        mobile = '1350114' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': image_code.upper()})

        self.assertEqual(sms_code_api.get_resp_code(), 200)
        sms_code = Redis().get_sms_code(mobile, type='xg')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

    def test_send_xg_sms_code_image_code_lower(self):
        """
        测试图形验证码小写情况下短信发送成功
        :return:
        """
        mobile = '1350214' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': image_code.lower()})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='xg')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

    def test_send_xg_sms_code_fast(self):
        """
        测试发送验证码成功后，1分钟内不可再次获取
        :return:
        """
        mobile = '1350104' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='xg')
        self.assertEqual(len(sms_code), 4)
        self.assertTrue(sms_code.isdigit())

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 101)
        self.assertEqual(sms_code_api.get_resp_message(), u'短信已发送,请稍等,如未收到,请在1分钟后重新发送!')

    def test_send_xg_sms_code_mobile_error(self):
        """
        测试请求接口手机号位数不正确
        :return:
        """
        mobile = '1350114'
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 424)
        self.assertEqual(sms_code_api.get_resp_message(),u'手机号格式错误!')

    @unittest.skip(reason=settings.SKIP_REASON)
    def test_send_xg_sms_code_mobile_null(self):
        """
        测试请求接口手机号为None
        :return:
        """
        mobile = '1350105' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': None, 'type': 'xg_sms_code', 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

    @unittest.skip(reason=settings.SKIP_REASON)
    def test_send_xg_sms_code_type_null(self):
        """
        测试请求接口类型为None
        :return:
        """
        mobile = '1350106' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': None, 'img_code': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

    @unittest.skip(reason=settings.SKIP_REASON)
    def test_send_xg_sms_code_image_code_null(self):
        """
        测试请求接口图形验证码为None
        :return:
        """
        mobile = '1350107' + str(random.randint(1111, 9999))
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'xg_sms_code', 'img_code': None})

        self.assertEqual(sms_code_api.get_resp_code(), 200)
