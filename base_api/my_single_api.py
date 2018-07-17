# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class MySingleApi(LoginBaseApi):
    """
我的单买(自买)记录列表（待开奖、已中奖、未中奖）

0待开奖
1未中奖
2中小奖
3中大奖
默认为全部

    """
    url = "/info/mySingle"

    def build_custom_param(self, data):
        return {'status':data['status'],'page': 1, 'length': 20}
