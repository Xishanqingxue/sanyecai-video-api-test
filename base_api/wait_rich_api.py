# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class WaitRichApi(LoginBaseApi):
    """
    等待开奖队列
    """
    url = "/tabu/waitRich"

    def build_custom_param(self, data):
        return {'roomId':data['roomId']}

