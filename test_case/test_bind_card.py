# -*- coding:utf-8 -*-
from base_api.send_message_api import LoginSendMessageApi
from base_api.image_code_api import ImageCodeApi
from base_api.bind_card_api import BindCardApi
from utilities.mysql_helper import MysqlHelper
from base_api.bind_card_list_api import BindingListApi
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
import random, json,time,settings


class TestBindCardApi(BaseCase):
    """
    绑定银行卡
    """
    not_authentication_union_id = 'dw_22017547'
    not_authentication_nickname = '彩票不差钱'
    not_authentication_head_pic = 'https://static.dwtv.tv/h5//images/default-header.png'
    mobile = '1511011' + str(random.randint(1111, 9999))

    def test_bind_card_success(self):
        """
        测试绑定银行卡成功
        :return:
        """
        mobile = '13501077762'
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'tj_sms_code', 'imgCode': image_code})

        sms_code = Redis().get_sms_code(mobile, type='tj')

        bind_card_api = BindCardApi()
        bind_card_api.get({'bindingType': 1, 'cardNum': '6228480018373695875', 'bankId': 2,
                           'mobile': mobile, 'verCode': sms_code, 'type': 'tj_sms_code'})
        self.assertEqual(bind_card_api.get_resp_code(), 200)

        # 获取绑定列表
        bind_list_api = BindingListApi()
        bind_list_api.get()
        self.assertEqual(bind_list_api.get_resp_code(), 200)
        self.assertEqual(bind_list_api.get_resp_message(), u'ok')

        result = bind_list_api.get_resp_result()[0]
        self.assertEqual(result['bankId'], 2)
        self.assertEqual(result['bindingType'], 1)
        self.assertEqual(result['cardNum'], u'6228480018373695875')
        self.assertEqual(result['bankName'], u'农业银行')

    def test_bind_card_mobile_error(self):
        """
        测试绑定银行卡绑定手机号不正确
        :return:
        """
        mobile = '13511114758'
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'tj_sms_code', 'imgCode': image_code})

        sms_code = Redis().get_sms_code(mobile, type='tj')

        bind_card_api = BindCardApi()
        bind_card_api.get({'bindingType': 1, 'cardNum': '6228480018373695875', 'bankId': 2,
                           'mobile': mobile, 'verCode': sms_code, 'type': 'tj_sms_code'})
        self.assertEqual(bind_card_api.get_resp_code(), 414)
        self.assertEqual(bind_card_api.get_resp_message(), '手机号码错误,请使用尾号: 7762的手机号进行验证!')

    def test_bind_card_not_auth(self):
        """
        测试未实名认证绑定银行卡
        :return:
        """
        mobile = '1870000' + str(random.randint(1111, 9999))
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id=self.not_authentication_union_id,
                                           nickname=self.not_authentication_nickname, source=1,
                                           head_pic=self.not_authentication_head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'tj_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='tj')

        bind_card_api = BindCardApi(union_id=self.not_authentication_union_id,
                                           nickname=self.not_authentication_nickname, source=1,
                                           head_pic=self.not_authentication_head_pic)
        bind_card_api.get({'bindingType': 1, 'cardNum': '6228480018373695875', 'bankId': 2,
                           'mobile': mobile, 'verCode': sms_code, 'type': 'tj_sms_code'})

        self.assertEqual(bind_card_api.get_resp_code(), 415)
        self.assertEqual(bind_card_api.get_resp_message(), u'未实名认证,请先实名认证再绑定!')

        # 获取绑定列表
        bind_list_api = BindingListApi(union_id=self.not_authentication_union_id,
                                           nickname=self.not_authentication_nickname, source=1,
                                           head_pic=self.not_authentication_head_pic)
        bind_list_api.get()
        self.assertEqual(bind_list_api.get_resp_code(), 200)
        self.assertEqual(bind_list_api.get_resp_message(), u'ok')
        self.assertEqual(bind_list_api.get_resp_result(), [])

    def test_bind_card_again(self):
        """
        测试绑定银行卡重复绑定
        :return:
        """
        mobile = '13501077762'
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'tj_sms_code', 'imgCode': image_code})

        sms_code = Redis().get_sms_code(mobile, type='tj')

        bind_card_api = BindCardApi()
        bind_card_api.get({'bindingType': 1, 'cardNum': '6228480018373695875', 'bankId': 2,
                           'mobile': mobile, 'verCode': sms_code, 'type': 'tj_sms_code'})

        self.assertEqual(bind_card_api.get_resp_code(), 200)

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': mobile, 'type': 'tj_sms_code', 'imgCode': image_code})

        sms_code = Redis().get_sms_code(mobile, type='tj')

        bind_card_api = BindCardApi()
        bind_card_api.get({'bindingType': 1, 'cardNum': '6228480018373695875', 'bankId': 2,
                           'mobile': mobile, 'verCode': sms_code, 'type': 'tj_sms_code'})

        self.assertEqual(bind_card_api.get_resp_code(), 407)
        self.assertEqual(bind_card_api.get_resp_message(), u'已绑定,无需再次绑定!')

    def tearDown(self):
        MysqlHelper().delete_bind_card(MysqlHelper().get_user_details()['auth_id'])
        time.sleep(1)
