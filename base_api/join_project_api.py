# -*- coding:utf-8 -*-
from base.base_api import BaseApi

class JoinProjectApi(BaseApi):
    """
    获取合买队列策略
    """
    url = "/info/joinProject"

    def build_custom_param(self, data):
        return {'projectId':data['projectId']}