# # -*- coding:utf-8 -*-
# from base_api.get_sell_lottery_api import GetSellLotteryApi
# from base.base_case_api import BaseCase
# from utilities.mysql_helper import MysqlHelper
# import json
#
#
# class TestGetSellLotteryApi(BaseCase):
#     """
#     获取在售彩种
#     """
#
#     def test_get_sell_lottery_success(self):
#         """
#         获取在售彩种
#         :return:
#         """
#
#         get_sell_lottery_api = GetSellLotteryApi()
#         get_sell_lottery_api.get()
#
#         self.assertEqual(get_sell_lottery_api.get_resp_code(),200)