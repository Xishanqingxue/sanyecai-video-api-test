# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class MyPrecentApi(LoginBaseApi):
    """
    获取提现记录
    """
    url = "/info/myPrecent"

    def build_custom_param(self, data):
        return {'page': 1, 'length': 20}
