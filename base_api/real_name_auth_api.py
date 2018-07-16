# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class RealNameAuthApi(LoginBaseApi):
    """
    实名认证
    """
    url = "/realNameAuth"

    def build_custom_param(self, data):
        return {'real_name': data['real_name'], 'mobile': data['mobile'], 'card_no': data['card_no'],
                'cardType': data['cardType'], 'verCode': data['verCode'],'type':data['type']}
