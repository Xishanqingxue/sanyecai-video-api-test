# -*- coding:utf-8 -*-
from base.base_api import BaseApi
from base.login_base import LoginBaseApi

class SendMessageApi(BaseApi):
    """
    发送短信验证码
    """
    url = "/finan/sendMessage"

    def build_custom_param(self, data):
        return {'mobile':data['mobile'],'type':data['type'],'imgCode':data['imgCode']}


class LoginSendMessageApi(LoginBaseApi):
    """
    发送短信验证码(登录)
    """
    url = "/finan/sendMessage"

    def build_custom_param(self, data):
        return {'mobile':data['mobile'],'type':data['type'],'imgCode':data['imgCode']}


class Send253MessageApi(BaseApi):
    """
    发送短信验证码
    """
    url = "/finan/send253Message"

    def build_custom_param(self, data):
        return {'mobile':data['mobile'],'type':data['type'],'imgCode':data['imgCode']}