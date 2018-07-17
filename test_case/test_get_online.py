# -*- coding:utf-8 -*-
from base_api.get_online_api import GetOnlineApi
from base.base_case_api import BaseCase
from utilities.mysql_helper import MysqlHelper
import time, re


class TestGetOnlineApi(BaseCase):
    """
    获取在线用户
    """

    def test_get_self_lott_success(self):
        """
        获取在线用户信息
        :return:
        """
        get_online = GetOnlineApi()
        get_online.get()
        self.assertEqual(get_online.get_resp_code(), 200)
        result = get_online.get_resp_result()
        id = result["user"]["id"]
        account_info = MysqlHelper().get_lot_account_info(user_id=id)

        self.assertEqual(result["account"][0]["balance"], account_info["balance"])
        account_type = account_info["account_type"]
        self.assertEqual(result["account"][0]["accountType"], account_type)
        user_info = MysqlHelper().get_lot_user_info(id)
        self.assertEqual(result["user"]["id"], user_info["id"])
        self.assertEqual(result["user"]["userName"], user_info["user_name"])
        self.assertEqual(result["user"]["password"], user_info["password"])
        self.assertEqual(result["user"]["email"], user_info["email"])
        self.assertEqual(result["user"]["userStatus"], user_info["user_status"])
        self.assertEqual(result["user"]["unionId"], user_info["union_id"])
        self.assertEqual(result["user"]["nickname"], user_info["nickname"])
        self.assertEqual(result["user"]["headPic"], user_info["head_pic"])
        self.assertEqual(result["user"]["platformId"], user_info["platform_id"])
        self.assertEqual(result["user"]["authId"], user_info["auth_id"])
        createTime = float(result["user"]["createTime"] / 1000)
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(createTime))
        num = re.compile(r'\d+')
        createTime = num.findall(create_time)
        create_time = num.findall(str(user_info["create_time"]))
        self.assertEqual(createTime, create_time)
        updateTime = float(result["user"]["updateTime"] / 1000)
        update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(updateTime))
        num = re.compile(r'\d+')
        updateTime = num.findall(update_time)
        update_time = num.findall(str(user_info["update_time"]))
        self.assertEqual(updateTime, update_time)
