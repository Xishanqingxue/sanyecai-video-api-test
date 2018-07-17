# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class BindCardApi(LoginBaseApi):
    """
    绑定银行卡
    """
    url = "/finan/bankCardBinding"

    def build_custom_param(self, data):
        return {'bindingType': data['bindingType'], 'cardNum': data['cardNum'], 'bankId': data['bankId'],
                'mobile': data['mobile'], 'verCode': data['verCode'], 'type': data['type']}
