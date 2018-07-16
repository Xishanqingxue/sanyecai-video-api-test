# -*- coding:utf-8 -*-
from base.base_api import BaseApi

class ImageCodeApi(BaseApi):
    """
    图形验证码
    """
    url = "/finan/getVCode"

    def build_custom_param(self, data):
        return {'mobile':data['mobile']}