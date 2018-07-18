# -*- coding:utf-8 -*-
from base.base_api import BaseApi

class GetSellLotteryApi(BaseApi):
    """
    获取在售彩种
    """
    url = "/bet/getSellLott"

    def build_custom_param(self, data):
        return {'roomId':data['roomId']}