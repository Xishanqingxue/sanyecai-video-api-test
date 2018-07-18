# -*- coding:utf-8 -*-
from base.base_api import BaseApi


class TodaySalesApi(BaseApi):
    """
    今日彩种销量榜
    """
    url = "/tabu/todaySales"

    def build_custom_param(self, data):
        return {'roomId':data['roomId'],'source':data['source']}

