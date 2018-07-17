# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi

class EditMobileApi(LoginBaseApi):
    """
    修改用户手机号
    """
    url = "/finan/editModel"

    def build_custom_param(self, data):
        return {'mobile':data['mobile'],'verCode':data['verCode'],'type':data['type']}
