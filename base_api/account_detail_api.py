# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi

class MyAcDetApi(LoginBaseApi):
    """
    获取用户账户变动记录信息
    """
    url = "/info/myAcDet"

    def build_custom_param(self, data):
        return {'unionId':data['unionId'],'source':data['source']}