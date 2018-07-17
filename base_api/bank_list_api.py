# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi

class BankListApi(LoginBaseApi):
    """
    获取银行列表
    """
    url = "/finan/queryBankList"
