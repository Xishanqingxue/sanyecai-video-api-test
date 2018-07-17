# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi

class GetUserInfo(LoginBaseApi):
    """
    获取用户信息
    """
    url = "/info/user"

    def build_custom_param(self, data):
        return {"unionId":data["unionId"],"source":data["source"]}