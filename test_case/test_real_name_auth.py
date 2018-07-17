# -*- coding:utf-8 -*-
from base_api.send_message_api import LoginSendMessageApi
from base_api.image_code_api import ImageCodeApi
from base_api.real_name_auth_api import RealNameAuthApi
from utilities.mysql_helper import MysqlHelper
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
import random,settings,json


class TestRealNameAuthApi(BaseCase):
    """
    实名认证
    """
    real_name = '刘祖全'
    card_number = '512501197203035172'
    card_number_x = '51052119850508797x'
    card_number_X = '51052119850508797X'
    head_pic = settings.TEST_HEAD_PIC

    def test_real_name_auth_success(self):
        """
        测试正常实名认证成功
        :return:
        """
        union_id = '00' + str(random.randint(1111111, 9999999))
        mobile = '1351112' + str(random.randint(1111, 9999))
        nickname = 'ceshi000001'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id,nickname=nickname,head_pic=self.head_pic,source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id,nickname=nickname,head_pic=self.head_pic,source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)
        self.assertEqual(real_name_api.get_resp_message(),"恭喜您!认证成功,可以正常购买彩票啦!")

    def test_real_name_auth_success_card_x(self):
        """
        测试身份证号中带小写x可以认证成功
        :return:
        """
        union_id = '01' + str(random.randint(1111111, 9999999))
        mobile = '1351122' + str(random.randint(1111, 9999))
        nickname = 'ceshi000002'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number_x,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)
        self.assertEqual(real_name_api.get_resp_message(), "恭喜您!认证成功,可以正常购买彩票啦!")

    def test_real_name_auth_success_card_X(self):
        """
        测试身份证号中带大写x可以认证成功
        :return:
        """
        union_id = '02' + str(random.randint(1111111, 9999999))
        mobile = '1351133' + str(random.randint(1111, 9999))
        nickname = 'ceshi000003'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number_X,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)
        self.assertEqual(real_name_api.get_resp_message(), "恭喜您!认证成功,可以正常购买彩票啦!")


    def test_real_name_auth_card_num_error(self):
        """
        测试绑定不存在的身份证
        :return:
        """
        union_id = '03' + str(random.randint(1111111, 9999999))
        mobile = '1351144' + str(random.randint(1111, 9999))
        nickname = 'ceshi000004'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': '370481200602058511',
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 419)
        self.assertEqual(real_name_api.get_resp_message(), "身份证号码格式有误!")

    def test_real_name_auth_sms_code_error(self):
        """
        测试手机验证码不正确
        :return:
        """
        union_id = '04' + str(random.randint(1111111, 9999999))
        mobile = '1351155' + str(random.randint(1111, 9999))
        nickname = 'ceshi000005'

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': '370481200602058511',
                           'cardType': 1, 'verCode': '1342', 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 413)
        self.assertEqual(real_name_api.get_resp_message(), "手机验证码错误!")

    def test_real_name_auth_again(self):
        """
        测试重复认证
        :return:
        """
        union_id = '05' + str(random.randint(1111111, 9999999))
        mobile = '1351166' + str(random.randint(1111, 9999))
        nickname = 'ceshi000006'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 200)
        self.assertEqual(real_name_api.get_resp_message(), "恭喜您!认证成功,可以正常购买彩票啦!")

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': self.card_number,
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 412)
        self.assertEqual(real_name_api.get_resp_message(), "已经认证,请勿重复认证!")

    def test_real_name_auth_not_18(self):
        """
        测试未满18岁
        :return:
        """
        union_id = '06' + str(random.randint(1111111, 9999999))
        mobile = '1351177' + str(random.randint(1111, 9999))
        nickname = 'ceshi000007'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': self.real_name, 'mobile': mobile, 'cardNo': '410223200202102231',
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 418)
        self.assertEqual(real_name_api.get_resp_message(), "未成年人不可购买彩票!")


    def test_real_name_is_exits(self):
        """
        测试绑定已经绑定的身份证号
        :return:
        """
        union_id = '07' + str(random.randint(1111111, 9999999))
        mobile = '1351188' + str(random.randint(1111, 9999))
        nickname = 'ceshi000008'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'rz_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='rz')

        real_name_api = RealNameAuthApi(union_id, nickname=nickname, head_pic=self.head_pic, source=1)
        real_name_api.get({'realName': '高英龙', 'mobile': mobile, 'cardNo': '370105199512046531',
                           'cardType': 1, 'verCode': sms_code, 'type': 'rz_sms_code'})

        self.assertEqual(real_name_api.get_resp_code(), 425)
        self.assertEqual(real_name_api.get_resp_message(), "输入的身份证号已绑定其他账号，请更换一个新的身份证号!")


    def tearDown(self):
        for x in [self.card_number_X,self.card_number_x,self.card_number]:
            MysqlHelper().delete_user_auth(x)