# -*- coding:utf-8 -*-
from base_api.send_message_api import LoginSendMessageApi
from base_api.image_code_api import ImageCodeApi
from base_api.real_name_auth_api import RealNameAuthApi
from base.login import LoginApi
from utilities.mysql_helper import MysqlHelper
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
import random,settings


class TestRealNameAuthApi(BaseCase):
    """
    实名认证
    """
    union_id = '8885'
    union_id_two = '8884'
    real_name = '刘祖全'
    card_number = '512501197203035172'
    mobile_list = []
    source = 1
    head_pic = settings.TEST_HEAD_PIC

    def test_real_name_auth_success(self):
        """
        测试短信验证码全大写实名认证成功
        :return:
        """
        mobile = '1351112' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name1'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(self.union_id,nickname=nickname, source=self.source,
                 head_pic=self.head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(self.union_id,nickname=nickname, source=self.source,
                 head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code.upper(), 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)

    def test_real_name_auth_success_card_x(self):
        """
        测试身份证号中带X可以认证成功
        :return:
        """
        mobile = '1351110' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name2'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': '51052119850508797x',
                           'cardType': 1, 'verCode': sms_code.upper(), 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)

    def test_real_name_auth_success_sms_code_lower(self):
        """
        测试短信验证码全小写实名认证成功
        :return:
        """
        mobile = '1351113' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name3'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code.lower(), 'type': 'rz_sms_code'})

    def test_real_name_auth_card_num_error(self):
        """
        测试绑定不存在的身份证
        :return:
        """
        mobile = '1351114' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name4'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': '370481200602058511',
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 419)
        self.assertEqual(real_name_api.get_resp_message(), u'身份证号码格式有误!')

    def test_real_name_auth_sms_code_error(self):
        """
        测试手机验证码不正确
        :return:
        """
        mobile = '1351115' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name5'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': '1342', 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 413)
        self.assertEqual(real_name_api.get_resp_message(), u'手机验证码错误!')

    def test_real_name_auth_again(self):
        """
        测试重复认证
        :return:
        """
        mobile = '1351116' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name6'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(self.union_id)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 412)
        self.assertEqual(real_name_api.get_resp_message(), u'已经认证,请勿重复认证!')

    def test_real_name_auth_not_18(self):
        """
        测试未满18岁
        :return:
        """
        mobile = '1351117' + str(random.randint(1111, 9999))
        self.mobile_list.append(mobile)
        nickname = 'real_name7'
        login_api = LoginApi()
        login_api.login(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)

        self.assertEqual(login_api.get_resp_code(), 200)
        self.assertEqual(login_api.get_resp_message(), u'success')

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(unionID=self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(self.union_id, source=1, nickname=nickname, head_pic=self.head_pic)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': '410223200202102231',
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 418)
        self.assertEqual(real_name_api.get_resp_message(), u'未满十八岁!')


    def tearDown(self):
        mysql = MysqlHelper()
        for x in self.mobile_list:
            mysql.delete_user_auth(x)
        mysql.delete_user(self.union_id)
