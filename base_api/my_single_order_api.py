# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class MySingleOrderApi(LoginBaseApi):
    """
获取用户单买(自买)订单记录信息

status
状态
否
int
0待开奖
1未中奖
2中小奖
3中大奖
默认为全部
    """
    url = "/info/mySingleOrder"

    def build_custom_param(self, data):
        return {'status':data['status'],'page': 1, 'length': 20}
