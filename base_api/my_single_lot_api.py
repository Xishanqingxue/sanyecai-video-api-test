# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class MySingleLotApi(LoginBaseApi):
    """
获取用户单买(自买)彩票情况

detailStatus
下单状态
否
int
0下单
1刮票成功
2失败
默认为全部

orderNo
订单号
否
String
订单号

bonusStatus
中将状态
否
int
0未中奖
1中奖


    """
    url = "/info/mySingleLot"

    def build_custom_param(self, data):
        return {'detailStatus': data['detailStatus'], 'orderNo': data['orderNo'], 'bonusStatus': data['bonusStatus'],
                'page': 1, 'length': 20}
