# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi
from base.base_api import BaseApi

class BetBetApi(LoginBaseApi):
    """
    购彩
    """
    url = "/bet/bet"

    def build_custom_param(self, data):
        return {'lotoId':data['lotoId'],'nums':data['nums'],'buyType':data['buyType'],
                'window':data['window'],'roomId':data['roomId'],'shareMethod':data['shareMethod'],
                'memberNum':data['memberNum'],'provinceId':data['provinceId']}

class BetBetApiNotLogin(BaseApi):
    """
    投注(未登录)
    """
    url = "/video-lottery-api/bet/bet"

    def build_custom_param(self, data):
        return {'lotoId':data['lotoId'],'nums':data['nums'],'buyType':data['buyType'],
                'window':data['window'],'roomId':data['roomId'],'shareMethod':data['shareMethod'],
                'memberNum':data['memberNum'],'provinceId':data['provinceId']}