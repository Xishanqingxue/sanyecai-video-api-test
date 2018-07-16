# -*- coding:utf-8 -*-
from base.login import LoginApi
from base.base_case_api import BaseCase
from utilities.mysql_helper import MysqlHelper
import json,settings


class TestLoginApi(BaseCase):
    """
    登录
    """
    user_nickname_not_auth = '夏夏夏夏夏'

    @classmethod
    def setUpClass(cls):
        MysqlHelper().fix_user_money(balance=0)
        MysqlHelper().delete_user(nickname=cls.user_nickname_not_auth)

    def test_login_success(self):
        """
        测试已实名用户登录成功
        """
        login_api = LoginApi()
        response = login_api.login()


        self.assertEqual(login_api.get_resp_code(),200)
        self.assertEqual(login_api.get_resp_message(),'success')

        result = json.loads(response.content)['result']
        self.assertEqual(result['userStatus'],1)
        self.assertEqual(result['unionId'],settings.TEST_UNION_ID)
        self.assertEqual(result['nickname'],settings.TEST_NICKNAME)
        self.assertEqual(result['headPic'],settings.TEST_HEAD_PIC)
        self.assertEqual(result['platformId'],settings.TEST_SOURCE)
        self.assertEqual(result['authId'],MysqlHelper().get_user_details()['auth_id'])
        self.assertIsNone(result['password'])
        self.assertIsNone(result['email'])

    # def test_not_auth_login_success(self):
    #     """
    #     测试首次登录注册用户
    #     """
    #     login_api = LoginApi()
    #     response = login_api.login(nickname=self.user_nickname_not_auth)
    #
    #
    #     self.assertEqual(login_api.get_resp_code(),200)
    #     self.assertEqual(login_api.get_resp_message(),'success')
    #
    #     result = json.loads(response.content)['result']
    #     self.assertEqual(result['id'],MysqlHelper().get_user_details(nickname=self.user_nickname_not_auth)['id'])
    #     self.assertEqual(result['userName'],MysqlHelper().get_user_details(nickname=self.user_nickname_not_auth)['user_name'])
    #     self.assertEqual(result['userStatus'],1)
    #     self.assertEqual(result['unionId'],MysqlHelper().get_user_details(nickname=self.user_nickname_not_auth)['union_id'])
    #     self.assertEqual(result['nickname'],MysqlHelper().get_user_details(nickname=self.user_nickname_not_auth)['nickname'])
    #     self.assertEqual(result['headPic'],MysqlHelper().get_user_details(nickname=self.user_nickname_not_auth)['head_pic'])
    #     self.assertEqual(result['platformId'],1)
    #     self.assertIsNone(result['authId'])
    #     self.assertIsNone(result['password'])
    #     self.assertIsNone(result['email'])


    @classmethod
    def tearDownClass(cls):
        MysqlHelper().fix_user_money(balance=0)
        MysqlHelper().delete_user(nickname=cls.user_nickname_not_auth)