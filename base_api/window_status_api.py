# -*- coding:utf-8 -*-
from base.base_api import BaseApi


class WindowStatusApi(BaseApi):
    """
    获取窗口当前状态
    """
    url = "/finan/getLiveWindowStatus"

    def build_custom_param(self, data):
        return {'id':data['id'],'platformId':data['platformId']}
