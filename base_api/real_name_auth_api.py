# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class RealNameAuthApi(LoginBaseApi):
    """
    实名认证
    """
    url = "/finan/realNameAuth"

    def build_custom_param(self, data):
        return {'realName': data['realName'], 'mobile': data['mobile'], 'cardNo': data['cardNo'],
                'cardType': data['cardType'], 'verCode': data['verCode'],'type':data['type']}
