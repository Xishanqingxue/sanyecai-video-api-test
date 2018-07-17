# -*- coding:utf-8 -*-
from base_api.withdraw_api import WithdrawApplyApi
from base_api.image_code_api import ImageCodeApi
from base_api.send_message_api import LoginSendMessageApi
from base_api.account_detail_api import MyAcDetApi
from base_api.my_precent_api import MyPrecentApi
from utilities.redis_helper import Redis
from base.base_case_api import BaseCase
from utilities.mysql_helper import MysqlHelper
import json,random,settings


class TestWithDrawApplyApi(BaseCase):
    """
    申请提现
    """
    head_pic = settings.TEST_HEAD_PIC
    auth_id = MysqlHelper().get_user_details()['auth_id']
    mobile = '13501077762'
    real_name = '刘祖全'
    card_number = '512501197203035172'

    def test_withdraw_apply_amount_less(self):
        """
        测试账户剩余提现额度不足时申请提现
        :return:
        """

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': self.mobile})

        image_code = Redis().get_image_code(self.mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': self.mobile, 'type': 'tx_sms_code', 'imgCode': image_code})


        sms_code = Redis().get_sms_code(self.mobile, type='tx')

        withdraw_api = WithdrawApplyApi()
        withdraw_api.get({'amount': 500, 'source': 1, 'mobile':self.mobile ,
                'verCode': sms_code, 'type': 'tx_sms_code','bindingId':2})
        self.assertEqual(withdraw_api.get_resp_code(),422)
        self.assertEqual(withdraw_api.get_resp_message(),u'账户剩余提现额度不足,请查看后重试!')

    def test_withdraw_apply_not_cre(self):
        """
        测试未实名用户请求提现
        :return:
        """

        union_id = '10' + str(random.randint(1111111, 9999999))
        mobile = '1311112' + str(random.randint(1111, 9999))
        nickname = 'ceshi100001'

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': mobile})

        image_code = Redis().get_image_code(mobile)
        sms_code_api = LoginSendMessageApi(union_id,nickname=nickname,head_pic=self.head_pic,source=1)
        sms_code_api.get({'mobile': mobile, 'type': 'tx_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)

        sms_code = Redis().get_sms_code(mobile, type='tx')

        withdraw_api = WithdrawApplyApi(union_id,nickname=nickname,head_pic=self.head_pic,source=1)
        withdraw_api.get({'amount': 500, 'source': 1, 'mobile':mobile ,
                'verCode': sms_code, 'type': 'tx_sms_code','bindingId':2})
        self.assertEqual(withdraw_api.get_resp_code(),415)
        self.assertEqual(withdraw_api.get_resp_message(),u'未实名认证,请先实名认证再绑定!')


    def test_withdraw_mobile_error(self):
        """
        测试提现手机号与绑定手机号不一致时申请提现
        :return:
        """
        withdraw_api = WithdrawApplyApi()
        withdraw_api.get({'amount': 500, 'source': 1, 'mobile': '13288888888',
                          'verCode': '1233', 'type': 'tx_sms_code', 'bindingId': 2})
        self.assertEqual(withdraw_api.get_resp_code(), 414)
        self.assertEqual(withdraw_api.get_resp_message(), u'手机号码错误,请使用尾号: 7762的手机号进行验证!')

    def test_withdraw_apply_amount_success_first(self):
        """
        测试当天首次申请提现100元成功
        :return:
        """
        Redis().fix_user_withdraw_times(self.auth_id,0)
        MysqlHelper().fix_user_money(balance=100)
        MysqlHelper().fix_user_withdraw_amount(auth_id=self.auth_id,amount=100)
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': self.mobile})

        image_code = Redis().get_image_code(self.mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': self.mobile, 'type': 'tx_sms_code', 'imgCode': image_code})

        sms_code = Redis().get_sms_code(self.mobile, type='tx')

        withdraw_api = WithdrawApplyApi()
        withdraw_api.get({'amount': 100, 'source': 1, 'mobile':self.mobile ,
                'verCode': sms_code, 'type': 'tx_sms_code','bindingId':2})
        self.assertEqual(withdraw_api.get_resp_code(),200)
        self.assertEqual(withdraw_api.get_resp_message(),u'提现申请成功,请等待管理员审核!')

        # 提现记录
        my_precent_api = MyPrecentApi()
        my_precent_api.get()

        self.assertEqual(my_precent_api.get_resp_code(),200)
        self.assertEqual(my_precent_api.get_resp_message(),u'success')

        result = my_precent_api.get_resp_result()
        self.assertEqual(len(result),1)
        self.assertIsNotNone(result[0]['presentRecordNo'])
        self.assertEqual(result[0]['authId'],self.auth_id)
        self.assertEqual(result[0]['amount'],100.0)
        self.assertEqual(result[0]['actualAmount'],100.0)
        self.assertIsNone(result[0]['amountOfCash'])
        self.assertEqual(result[0]['tip'],0.0)
        self.assertEqual(result[0]['presentRecordStatus'],0)
        self.assertIsNone(result[0]['presentRecordStatusPre'])
        self.assertEqual(result[0]['debitStatus'], u'1')
        self.assertEqual(result[0]['source'], 1)
        self.assertEqual(result[0]['notify'], 9)
        self.assertIsNone(result[0]['bak'])
        self.assertEqual(result[0]['realName'], u'高英龙')
        self.assertEqual(result[0]['mobile'], self.mobile)
        self.assertEqual(result[0]['bindingId'],2)

        # 账户变动记录
        my_ac_det_api = MyAcDetApi()
        my_ac_det_api.get({'unionId': MysqlHelper().get_user_details()['union_id'], 'source': 1})

        self.assertEqual(my_ac_det_api.get_resp_code(), 200)
        self.assertEqual(my_ac_det_api.get_resp_message(), u'success')

        result = my_ac_det_api.get_resp_result()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['user_id'], MysqlHelper().get_user_details()['id'])
        self.assertEqual(result[0]['tradeType'], 3)
        self.assertEqual(result[0]['amountS'], -100.0)
    #
    def test_withdraw_apply_amount_max_than_5000(self):
        """
        测试当天提现金额已达5000后申请提现失败
        :return:
        """
        Redis().fix_user_withdraw_times(self.auth_id,1)
        Redis().fix_user_withdraw_money_today(self.auth_id,500000)
        MysqlHelper().fix_user_money(balance=100)
        MysqlHelper().fix_user_withdraw_amount(auth_id=self.auth_id,amount=100)
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': self.mobile})

        image_code = Redis().get_image_code(self.mobile)
        sms_code_api = LoginSendMessageApi()
        sms_code_api.get({'mobile': self.mobile, 'type': 'tx_sms_code', 'imgCode': image_code})

        sms_code = Redis().get_sms_code(self.mobile, type='tx')

        withdraw_api = WithdrawApplyApi()
        withdraw_api.get({'amount': 100, 'source': 1, 'mobile':self.mobile ,
                'verCode': sms_code, 'type': 'tx_sms_code','bindingId':2})
        self.assertEqual(withdraw_api.get_resp_code(),423)
        self.assertEqual(withdraw_api.get_resp_message(),u'当天剩余提现额度不足,请明日重试!')

    def tearDown(self):
        MysqlHelper().fix_user_withdraw_amount(auth_id=self.auth_id,amount=0)
        MysqlHelper().delete_user_withdraw_log(auth_id=self.auth_id)
        MysqlHelper().delete_account_details(MysqlHelper().get_user_details()['id'])
        Redis().fix_user_withdraw_times(self.auth_id, 0)
        Redis().fix_user_withdraw_money_today(self.auth_id, 0)
