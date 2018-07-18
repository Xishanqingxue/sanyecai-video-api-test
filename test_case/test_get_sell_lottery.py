# -*- coding:utf-8 -*-
from base_api.get_sell_lottery_api import GetSellLotteryApi
from base.base_case_api import BaseCase
from utilities.mysql_helper import MysqlHelper
import json,settings


class TestGetSellLotteryApi(BaseCase):
    """
    获取在售彩种
    """

    def test_get_sell_lottery_success(self):
        """
        获取在售彩种
        :return:
        """

        get_sell_lottery_api = GetSellLotteryApi()
        get_sell_lottery_api.get({'roomId':settings.DW_ROOM_ID})

        self.assertEqual(get_sell_lottery_api.get_resp_code(),200)

        result = get_sell_lottery_api.get_resp_result()

        db_sell_lottery = MysqlHelper().get_sell_lottery(room_id=settings.DW_ROOM_ID)

        self.assertEqual(len(result),len(db_sell_lottery))

        result_lottery_id = [i['id'] for i in result]
        db_sell_lottery_id = [i['lottery_id'] for i in db_sell_lottery]

        self.assertEqual(result_lottery_id,db_sell_lottery_id)

