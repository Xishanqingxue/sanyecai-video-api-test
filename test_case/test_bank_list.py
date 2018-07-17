# -*- coding:utf-8 -*-
from base_api.bank_list_api import BankListApi
from base.base_case_api import BaseCase
from utilities.mysql_helper import MysqlHelper
import settings


class TestBankListApi(BaseCase):
    """
    银行列表
    """

    def test_get_bank_list_success(self):
        """
        测试获取银行列表成功
        :return:
        """
        bank_id = []
        bank_name = []
        bank_list_api = BankListApi()
        bank_list_api.get()
        self.assertEqual(bank_list_api.get_resp_code(), 200)
        self.assertEqual(bank_list_api.get_resp_message(), u'查询成功')
        bank_list = bank_list_api.get_resp_result()
        for x in bank_list:
            bank_id.append(x['id'])
            bank_name.append(x['bankName'])

        db_bank_id = []
        db_bank_name = []
        db_bank_list = MysqlHelper().get_bank_list()
        for x in db_bank_list:
            db_bank_id.append(x['id'])
            db_bank_name.append(x['bank_name'])

        for x in bank_id:
            self.assertIn(x, db_bank_id)
        for x in bank_name:
            self.assertIn(x, db_bank_name)
