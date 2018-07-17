# -*- coding:utf-8 -*-
from base_api.send_message_api import SendMessageApi
from base_api.image_code_api import ImageCodeApi
from base_api.edit_mobile_api import EditMobileApi
from utilities.mysql_helper import MysqlHelper as mysql
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
import random,time,json


class TestEditMobileApi(BaseCase):
    """
    修改绑定手机号
    """
    auth_id = mysql().get_user_details()['auth_id']
    old_mobile = '13501077762'

    def test_edit_mobile_success(self):
        """
        测试修改绑定手机号成功
        :return:
        """
        new_mobile = '1581111' + str(random.randint(2222, 9999))
        # 验证原手机号
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': self.old_mobile})

        image_code = Redis().get_image_code(self.old_mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': self.old_mobile, 'type': 'xg_sms_code', 'imgCode': image_code})
        # self.assertEqual(sms_code_api.get_resp_code(), 200)
        sms_code = Redis().get_sms_code(self.old_mobile, type='xg')

        edit_mobile_api = EditMobileApi()
        edit_mobile_api.get({'mobile':self.old_mobile,'verCode':sms_code,'type':'xg_sms_code'})

        self.assertEqual(edit_mobile_api.get_resp_code(),200)

        # 绑定新手机号
        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': new_mobile})

        image_code = Redis().get_image_code(new_mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': new_mobile, 'type': 'xg_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)
        sms_code = Redis().get_sms_code(new_mobile, type='xg')

        edit_mobile_api = EditMobileApi()
        edit_mobile_api.get({'mobile': new_mobile, 'verCode': sms_code, 'type': 'xg_sms_code'})

        self.assertEqual(edit_mobile_api.get_resp_code(), 200)

        self.assertEqual(new_mobile,mysql().get_user_auth(self.auth_id)['mobile'])

    def test_edit_mobile_old_mobile_error(self):
        """
        测试请求接口原手机号错误
        :return:
        """
        new_mobile = '1581111' + str(random.randint(2222, 9999))

        image_code_api = ImageCodeApi()
        image_code_api.get({'mobile': new_mobile})

        image_code = Redis().get_image_code(new_mobile)
        sms_code_api = SendMessageApi()
        sms_code_api.get({'mobile': new_mobile, 'type': 'xg_sms_code', 'imgCode': image_code})

        self.assertEqual(sms_code_api.get_resp_code(), 200)
        sms_code = Redis().get_sms_code(new_mobile, type='xg')

        edit_mobile_api = EditMobileApi()
        edit_mobile_api.get({'mobile':new_mobile,'verCode':sms_code,'type':'xg_sms_code'})

        self.assertEqual(edit_mobile_api.get_resp_code(),414)
        self.assertEqual(edit_mobile_api.get_resp_message(),u'原手机号错误,请重新填写!')


    def tearDown(self):
        mysql().fix_user_mobile(self.auth_id,mobile=self.old_mobile)
        time.sleep(1.5)
