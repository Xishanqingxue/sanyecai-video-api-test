# -*- coding:utf-8 -*-
from base_api.bet_api import BetApi
from base_api.get_sell_lottery_api import GetSellLotteryApi
from base.base_case_api import BaseCase
from utilities.redis_helper import Redis
from utilities.mysql_helper import MysqlHelper
from base_api.account_detail_api import MyAcDetApi
from base_api.my_single_api import MySingleApi
from base_api.my_single_order_api import MySingleOrderApi
from base_api.window_status_api import WindowStatusApi
from base_api.my_single_lot_api import MySingleLotApi
from base.base_helper import send_prize
from base_api.today_sales_api import TodaySalesApi
from base_api.wait_rich_api import WaitRichApi
from base_api.get_online_api import GetOnlineApi
import time,json,random
import settings,requests


class TestBetSingleApi(BaseCase):
    """
    测试单人购彩流程
    """
    union_id = MysqlHelper().get_user_details()['union_id']
    user_id = MysqlHelper().get_user_details()['id']
    nickname = MysqlHelper().get_user_details()['nickname']
    auth_id = MysqlHelper().get_user_details()['auth_id']
    lottery_id = None
    lottery_amount = 0
    window_id = None
    station_number = None
    lottery_details = None
    room_id = settings.DW_ROOM_ID
    source = 1

    def setUp(self):
        # 调用获取在售彩种接口获取当前在售的彩种
        get_sell_lottery_api = GetSellLotteryApi()
        get_sell_lottery_api.get({'roomId':settings.DW_ROOM_ID})
        
        self.assertEqual(get_sell_lottery_api.get_resp_code(),200)
        result = get_sell_lottery_api.get_resp_result()
        index = random.randint(0, len(result) - 1)
        if len(result) == 0:
            pass
        else:

            self.lottery_id = result[index]['id']
            self.lottery_amount = result[index]['denomination']

        self.lottery_details  = MysqlHelper().get_lottery_detail(self.lottery_id)

        Redis().fix_stock_day_cache(self.lottery_id,9999) # 保证库存充足
        MysqlHelper().fix_stock_user() # 保证所有工位上所有票种数量充足
        MysqlHelper().fix_user_money(balance=0)


    def action(self,**kwargs):
        """
        测试单买一张未中奖
        :return:
        """
        flag = None
        num = kwargs['nums']
        win_amount = kwargs['win_amount']
        detail_id = []
        MysqlHelper().fix_user_money(balance=self.lottery_amount * num)
        bet_numbers = Redis().get_stock_day_cache(lottery_id=self.lottery_id) # 下单前获取彩种库存
        time.sleep(0.3)

        today_sales_api = TodaySalesApi()
        today_sales_api.get({'roomId': self.room_id, 'source': self.source})

        self.assertEqual(today_sales_api.get_resp_code(), 200)
        result = today_sales_api.get_resp_result()
        sales_before_bet = None
        big_award_before = None
        if self.lottery_details['lottery_name'] in str(result):
            for x in result:
                if x['lotteryName'] == self.lottery_details['lottery_name']:
                    sales_before_bet = x['sales']
                    img_url = x['imGurl']

                    response = requests.get(url=img_url)
                    self.assertEqual(response.status_code,200)
                    big_award_before = x['bigAward']
        else:
            flag = False

        # 下单 ----------------------------------------------------------------------
        bet_api = BetApi()
        bet_api.get({"lotoId": self.lottery_id, "nums": num, "buyType": 0, "window": 0,"shareMethod": None,
             "memberNum": None, 'provinceId': None,'roomId':self.room_id,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 200)
        self.assertEqual(bet_api.get_resp_message(), u"下单成功")

        after_bet_numbers = Redis().get_stock_day_cache(lottery_id=self.lottery_id) # 下单成功后获取彩种库存
        self.assertEqual(int(bet_numbers) - int(after_bet_numbers), num)
        time.sleep(3)

        order_detail = MysqlHelper().get_order_detail(user_id=self.user_id)
        if order_detail['window'] == None and order_detail['station_num'] == None:

            # 单买等待队列
            wait_rich_api = WaitRichApi()
            wait_rich_api.get({'roomId': self.room_id})
            self.assertEqual(wait_rich_api.get_resp_code(), 200)

            result = wait_rich_api.get_resp_result()
            if self.nickname in str(result):
                for x in result:
                    if x['nickname'] == self.nickname:
                        self.assertEqual(x['num'], num)
                        self.assertEqual(x['window'], 0)
                        self.assertEqual(x['orderStatus'], 0)
            else:
                self.assertTrue(False, msg='单买待开奖区无该用户数据！')

            self.assertFalse(True,msg='没有空闲的窗口或工位！')
        else:
            self.station_number = order_detail['station_num']

        # 获取窗口状态----------------------------------------------------------------------
        count = 1
        max_count = 20
        while count < max_count:
            window_status_api = WindowStatusApi()
            window_status_api.get({'id':settings.DW_ROOM_ID,'platformId':1})

            self.assertEqual(window_status_api.get_resp_code(),200)
            window_status_result = window_status_api.get_resp_result()

            window_nickname_list = [x['nickName'] for x in window_status_result]
            if settings.TEST_NICKNAME in window_nickname_list:

                for x in window_status_result:
                    if x['nickName'] == settings.TEST_NICKNAME:
                        self.window_id =x['num']
                        self.assertEqual(x['headPic'],settings.TEST_HEAD_PIC)
                        self.assertEqual(x['buyType'],0)
                        self.assertEqual(x['lotName'],self.lottery_details['lottery_name'])
                        self.assertEqual(int(x['roomId']),int(settings.DW_ROOM_ID))
                        self.assertEqual(x['window_level'],1)
                        self.assertEqual(x['label'],'单')
                        self.assertEqual(x['status'],'4')
                        self.assertIsNotNone(x['cameraUrl'])
                break
            else:
                time.sleep(1)
                count += 1
        self.assertLess(count,max_count)

        # 校验用户账户资金
        get_online_api = GetOnlineApi()
        get_online_api.get()
        self.assertEqual(get_online_api.get_resp_code(),200)

        result = get_online_api.get_resp_result()
        account = result['account']
        balance = None
        purchase_gold = None
        for x in account:
            if x['accountType'] == 1:
                balance = x['balance']
            if x['accountType'] == 2:
                purchase_gold = x['balance']
        self.assertEqual(int(purchase_gold),0)
        self.assertEqual(int(balance),0)

        # 单买等待队列
        wait_rich_api = WaitRichApi()
        wait_rich_api.get({'roomId':self.room_id})
        self.assertEqual(wait_rich_api.get_resp_code(),200)

        result = wait_rich_api.get_resp_result()
        if self.nickname in str(result):
            for x in result:
                if x['nickname'] == self.nickname:
                    self.assertEqual(x['num'],num)
                    self.assertNotEqual(x['window'],0)
                    self.assertEqual(x['orderStatus'],1)
        else:
            self.assertTrue(False,msg='单买待开奖区无该用户数据！')

        # 我得单买记录列表---待开奖----------------------------------------------------------------------
        my_single_api = MySingleApi()
        my_single_api.get({'status': 0})

        self.assertEqual(my_single_api.get_resp_code(),200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result),1)

        single_details = my_single_result[0]

        self.assertEqual(int(single_details['lotteryId']),int(self.lottery_id))
        self.assertEqual(single_details['userId'],self.user_id)
        self.assertEqual(single_details['userName'],MysqlHelper().get_user_details()['user_name'])
        self.assertEqual(single_details['lotteryName'],self.lottery_details['lottery_name'])
        self.assertEqual(single_details['buyType'],0)
        self.assertEqual(single_details['orderStatus'],1)
        self.assertEqual(single_details['num'],num)
        self.assertEqual(int(single_details['amount']),int(self.lottery_details['denomination']) * num)
        self.assertEqual(int(single_details['source']),int(self.source))
        self.assertEqual(int(single_details['roomId']),int(self.room_id))
        self.assertIsNotNone(single_details['window'])
        self.assertIsNotNone(single_details['stationNum'])
        self.assertIsNone(single_details['bonusAmount'])
        self.assertIsNone(single_details['bonus'])
        self.assertIsNone(single_details['bonusStatus'])

        self.assertIsNone(single_details['startTime'])
        self.assertIsNone(single_details['endTime'])
        self.assertIsNone(single_details['backAmount'])
        self.assertIsNone(single_details['actualBonus'])
        self.assertIsNone(single_details['bonusAmount'])
        self.assertIsNone(single_details['projectId'])
        self.assertIsNone(single_details['refund'])
        self.assertIsNone(single_details['bonus'])
        self.assertIsNone(single_details['bak'])
        self.assertIsNone(single_details['nikeName'])
        self.assertIsNone(single_details['headlogo'])
        self.assertIsNone(single_details['name'])
        self.assertIsNone(single_details['openId'])
        self.assertIsNone(single_details['drawType'])
        self.assertIsNone(single_details['memberNum'])
        self.assertIsNone(single_details['outTradeNo'])
        self.assertIsNone(single_details['ticketNo'])
        self.assertIsNotNone(single_details['orderNo'])
        self.assertEqual(int(single_details['lotteryId']),int(self.lottery_id))

        od_list = single_details['odList']
        for x in od_list:
            self.assertEqual(x['detailStatus'],0)
            self.assertEqual(x['amount'],self.lottery_details['denomination'])
            self.assertEqual(x['stationNumber'],self.station_number)
            self.assertIsNone(x['ticketNo'])
            self.assertIsNone(x['bonusStatus'])
            self.assertIsNone(x['bonusAmount'])
            self.assertIsNone(x['route'])

            self.assertIsNone(x['lotteryName'])
            self.assertIsNone(x['lotteryId'])
            self.assertIsNone(x['lottery'])
            self.assertIsNone(x['isUpload'])

            detail_id.append(x['id'])

        # 我得单买记录列表---未中奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 1})

        self.assertEqual(my_single_api.get_resp_code(),200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result),0)

        # 我得单买记录列表---中小奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 2})

        self.assertEqual(my_single_api.get_resp_code(),200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result),0)

        # 我得单买记录列表---中大奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 3})

        self.assertEqual(my_single_api.get_resp_code(),200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result),0)

        # 单买订单信息---待开奖----------------------------------------------------------------------
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status':0})
        self.assertEqual(my_single_order_api.get_resp_code(),200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result),1)
        self.assertEqual(my_single_order_result[0]['buyType'],0)
        self.assertEqual(int(my_single_order_result[0]['amount']),int(self.lottery_details['denomination']) * num)
        self.assertEqual(my_single_order_result[0]['num'],num)
        self.assertEqual(my_single_order_result[0]['orderStatus'],1)
        self.assertEqual(my_single_order_result[0]['denomination'],self.lottery_details['denomination'])
        self.assertEqual(my_single_order_result[0]['lotteryName'],self.lottery_details['lottery_name'])
        self.assertEqual(my_single_order_result[0]['maxBonus'],self.lottery_details['max_bonus'])

        self.assertLessEqual(int(time.time()) - int(my_single_order_result[0]['createTime']), 15)
        self.assertIsNotNone(my_single_order_result[0]['orderNo'])


        order_no = my_single_order_result[0]['orderNo']

        # 单买订单信息---未中奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 1})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买订单信息---中小奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 2})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买订单信息---中大奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 3})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买记录详情----------------------------------------------------------------------
        my_single_lottery_api = MySingleLotApi()
        my_single_lottery_api.get({'detailStatus': 0, 'orderNo': None, 'bonusStatus': None})

        self.assertEqual(my_single_lottery_api.get_resp_code(), 200)

        my_single_lottery_result = my_single_lottery_api.get_resp_result()
        self.assertEqual(len(my_single_lottery_result),num)

        result = my_single_lottery_result[0]
        self.assertEqual(result['detailStatus'],0)
        self.assertEqual(result['amount'],self.lottery_amount)
        self.assertIsNone(result['bonusStatus'])
        self.assertIsNone(result['bonusAmount'])
        self.assertIsNone(result['bonusTime'])
        self.assertIsNone(result['ticketNo'])
        self.assertIsNone(result['route'])
        self.assertEqual(result['isUpload'],0)
        self.assertIsNotNone(result['stationNumber'])

        lottery = result['lottery']
        self.assertEqual(lottery['lotteryName'],self.lottery_details['lottery_name'])
        self.assertEqual(lottery['denomination'],self.lottery_details['denomination'])
        self.assertEqual(lottery['maxReceiveNums'],self.lottery_details['max_receive_nums'])
        self.assertEqual(lottery['maxBonus'],self.lottery_details['max_bonus'])
        self.assertEqual(lottery['provinceId'],self.lottery_details['province_id'])
        self.assertEqual(lottery['salesStatus'],self.lottery_details['sales_status'])
        self.assertIsNone(lottery['abbr'])
        self.assertIsNone(lottery['name'])
        self.assertIsNone(lottery['stock'])
        self.assertIsNone(lottery['imgUrl'])

        # 用户账户记录----------------------------------------------------------------------
        my_ac_det_api = MyAcDetApi()
        my_ac_det_api.get({'unionId': self.union_id, 'source': 1})

        self.assertEqual(my_ac_det_api.get_resp_code(), 200)
        self.assertEqual(my_ac_det_api.get_resp_message(),u'success')

        result = my_ac_det_api.get_resp_result()
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['user_id'], MysqlHelper().get_user_details()['id'])
        self.assertEqual(result[0]['tradeType'], 2)
        self.assertEqual(str(result[0]['amountS']), '-{0}.0'.format(int(self.lottery_details['denomination']) * num))


        # 开奖---未中奖----------------------------------------------------------------------*****************************

        for x in detail_id:
            send_prize(detail_id=x,win_amount=win_amount)
            time.sleep(7) # 开奖预留时间

        # 开奖后获取当前窗口状态----------------------------------------------------------------------
        window_status_api = WindowStatusApi()
        window_status_api.get({'id': settings.DW_ROOM_ID, 'platformId': 1})

        self.assertEqual(window_status_api.get_resp_code(), 200)
        window_status_result = window_status_api.get_resp_result()

        window_nickname_list = [x['nickName'] for x in window_status_result]

        self.assertNotIn(settings.TEST_NICKNAME,window_nickname_list)

        # 我得单买记录列表---待开奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 0})

        self.assertEqual(my_single_api.get_resp_code(),200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result),0)

        # 单买订单信息---待开奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 0})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        if win_amount == 0:

            # 我得单买记录列表---中小奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 2})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result), 0)

            # 我得单买记录列表---中大奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 3})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result), 0)

            # 我得单买记录列表---未中奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 1})

            self.assertEqual(my_single_api.get_resp_code(),200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result),1)

            single_details = my_single_result[0]

            self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))
            self.assertEqual(single_details['userId'], self.user_id)
            self.assertEqual(single_details['userName'], MysqlHelper().get_user_details()['user_name'])
            self.assertEqual(single_details['lotteryName'], self.lottery_details['lottery_name'])
            self.assertEqual(single_details['buyType'], 0)
            self.assertEqual(single_details['orderStatus'], 2)
            self.assertEqual(single_details['num'], 1)
            self.assertEqual(int(single_details['amount']), self.lottery_details['denomination'])
            self.assertEqual(int(single_details['source']), int(self.source))
            self.assertEqual(int(single_details['roomId']), int(self.room_id))
            self.assertIsNotNone(single_details['window'])
            self.assertIsNotNone(single_details['stationNum'])
            self.assertEqual(single_details['bonusAmount'],0.0)
            self.assertEqual(single_details['bonus'],1)
            self.assertEqual(single_details['bonusStatus'],1)

            self.assertIsNone(single_details['startTime'])
            self.assertIsNone(single_details['endTime'])
            self.assertIsNone(single_details['backAmount'])
            self.assertEqual(single_details['actualBonus'],0.0)
            self.assertEqual(single_details['bonusAmount'],0.0)
            self.assertIsNone(single_details['projectId'])
            self.assertIsNone(single_details['refund'])
            self.assertEqual(single_details['bonus'],1)
            self.assertIsNone(single_details['bak'])
            self.assertIsNone(single_details['nikeName'])
            self.assertIsNone(single_details['headlogo'])
            self.assertIsNone(single_details['name'])
            self.assertIsNone(single_details['openId'])
            self.assertIsNone(single_details['drawType'])
            self.assertIsNone(single_details['memberNum'])
            self.assertIsNone(single_details['outTradeNo'])
            self.assertIsNone(single_details['ticketNo'])
            self.assertIsNotNone(single_details['orderNo'])
            self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))

            od_list = single_details['odList'][0]
            self.assertEqual(od_list['detailStatus'], 1)
            self.assertEqual(od_list['amount'], self.lottery_details['denomination'])
            self.assertIsNotNone(od_list['stationNumber'])
            self.station_number = od_list['stationNumber']  # 获取刮票工位
            self.assertIsNotNone(od_list['ticketNo'])
            self.assertEqual(od_list['bonusStatus'],0)
            self.assertEqual(od_list['bonusAmount'],0.0)
            self.assertIsNotNone(od_list['route'])

            self.assertIsNone(od_list['lotteryName'])
            self.assertIsNone(od_list['lotteryId'])
            self.assertIsNone(od_list['lottery'])
            self.assertIsNone(od_list['isUpload'])

            # 单买订单信息---中小奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 2})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 0)

            # 单买订单信息---中大奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 3})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 0)

            # 单买订单信息---未中奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 1})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 1)

            self.assertEqual(len(my_single_order_result), 1)
            self.assertEqual(my_single_order_result[0]['buyType'], 0)
            self.assertEqual(my_single_order_result[0]['amount'], self.lottery_details['denomination'])
            self.assertLessEqual(int(time.time()) - int(my_single_order_result[0]['createTime']), 15)
            self.assertEqual(my_single_order_result[0]['num'], 1)
            self.assertIsNotNone(my_single_order_result[0]['orderNo'])
            self.assertEqual(my_single_order_result[0]['actualBonus'], 0.0)
            self.assertEqual(my_single_order_result[0]['bonusStatus'], 1)
            self.assertEqual(my_single_order_result[0]['bonus'], 1)
            self.assertEqual(my_single_order_result[0]['maxBonus'], self.lottery_details['max_bonus'])
            self.assertEqual(my_single_order_result[0]['orderStatus'], 2)
            self.assertEqual(my_single_order_result[0]['denomination'], self.lottery_details['denomination'])
            self.assertEqual(my_single_order_result[0]['lotteryName'], self.lottery_details['lottery_name'])

            # 单买记录详情----------------------------------------------------------------------
            my_single_lottery_api = MySingleLotApi()
            my_single_lottery_api.get({'detailStatus': 1, 'orderNo': order_no, 'bonusStatus': 0})

            self.assertEqual(my_single_lottery_api.get_resp_code(), 200)

            my_single_lottery_result = my_single_lottery_api.get_resp_result()[0]

            self.assertEqual(my_single_lottery_result['detailStatus'], 1)
            self.assertEqual(my_single_lottery_result['amount'], self.lottery_details['denomination'])
            self.assertEqual(my_single_lottery_result['bonusStatus'], 0)
            self.assertEqual(my_single_lottery_result['bonusAmount'], 0.0)
            self.assertNotEqual(my_single_lottery_result['bonusTime'], my_single_lottery_result['createTime'])
            self.assertIsNotNone(my_single_lottery_result['ticketNo'])
            self.assertIsNotNone(my_single_lottery_result['route'])
            self.assertEqual(my_single_lottery_result['isUpload'], 1)
            self.assertIsNotNone(my_single_lottery_result['stationNumber'])
            self.assertEqual(int(my_single_lottery_result['lotteryId']), int(self.lottery_id))
            self.assertIsNone(my_single_lottery_result['lotteryName'], 1)
            lottery = my_single_lottery_result['lottery']
            self.assertEqual(lottery['lotteryName'], self.lottery_details['lottery_name'])
            self.assertEqual(lottery['denomination'], self.lottery_details['denomination'])
            self.assertEqual(lottery['maxReceiveNums'], self.lottery_details['max_receive_nums'])
            self.assertEqual(lottery['maxBonus'], self.lottery_details['max_bonus'])
            self.assertEqual(lottery['provinceId'], self.lottery_details['province_id'])
            self.assertEqual(lottery['salesStatus'], self.lottery_details['sales_status'])
            self.assertIsNone(lottery['abbr'])
            self.assertIsNone(lottery['name'])
            self.assertIsNone(lottery['stock'])
            self.assertIsNone(lottery['imgUrl'])

            # 获取今日彩种销量榜数据
            today_sales_api = TodaySalesApi()
            today_sales_api.get({'roomId':self.room_id,'source':self.source})

            self.assertEqual(today_sales_api.get_resp_code(),200)
            result = today_sales_api.get_resp_result()
            if self.lottery_details['lottery_name'] in str(result):
                for x in result:
                    if x['lotteryName'] == self.lottery_details['lottery_name']:
                        sales_after_bet = x['sales']
                        big_award_after = x['bigAward']

                        if flag == False:
                            self.assertEqual(int(sales_after_bet),num)
                            self.assertEqual(int(big_award_after),0)
                        else:
                            self.assertEqual(int(sales_after_bet) - int(sales_before_bet), num)
                            self.assertEqual(big_award_after, big_award_before)
            else:
                self.assertTrue(False,msg='今日彩种销量榜未出现该彩种！')

            # 校验用户账户资金
            get_online_api = GetOnlineApi()
            get_online_api.get({'roomId':self.room_id})
            self.assertEqual(get_online_api.get_resp_code(), 200)

            result = get_online_api.get_resp_result()
            account = result['account']
            balance = None
            purchase_gold = None
            for x in account:
                if x['accountType'] == 1:
                    balance = x['balance']
                if x['accountType'] == 2:
                    purchase_gold = x['balance']
            self.assertEqual(int(purchase_gold), 0)
            self.assertEqual(int(balance), 0)

        elif 10000 > win_amount > 0:
            # 我得单买记录列表---中小奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 2})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result), 1)

            single_details = my_single_result[0]

            self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))
            self.assertEqual(single_details['userId'], self.user_id)
            self.assertEqual(single_details['userName'], MysqlHelper().get_user_details()['user_name'])
            self.assertEqual(single_details['lotteryName'], self.lottery_details['lottery_name'])
            self.assertEqual(single_details['buyType'], 0)
            self.assertEqual(single_details['orderStatus'], 2)
            self.assertEqual(single_details['num'], num)
            self.assertEqual(int(single_details['amount']), int(self.lottery_details['denomination']) * num)
            self.assertEqual(int(single_details['source']), int(self.source))
            self.assertEqual(int(single_details['roomId']), int(self.room_id))
            self.assertIsNotNone(single_details['window'])
            self.assertIsNotNone(single_details['stationNum'])
            self.assertEqual(int(single_details['bonusAmount']), win_amount * num)
            self.assertEqual(single_details['bonus'], 1)
            self.assertEqual(single_details['bonusStatus'], 2)

            self.assertIsNone(single_details['startTime'])
            self.assertIsNone(single_details['endTime'])
            self.assertIsNone(single_details['backAmount'])
            self.assertEqual(int(single_details['actualBonus']), win_amount * num)
            self.assertEqual(int(single_details['bonusAmount']), win_amount * num)
            self.assertIsNone(single_details['projectId'])
            self.assertIsNone(single_details['refund'])
            self.assertEqual(single_details['bonus'], 1)
            self.assertIsNone(single_details['bak'])
            self.assertIsNone(single_details['nikeName'])
            self.assertIsNone(single_details['headlogo'])
            self.assertIsNone(single_details['name'])
            self.assertIsNone(single_details['openId'])
            self.assertIsNone(single_details['drawType'])
            self.assertIsNone(single_details['memberNum'])
            self.assertIsNone(single_details['outTradeNo'])
            self.assertIsNone(single_details['ticketNo'])
            self.assertIsNotNone(single_details['orderNo'])
            self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))

            od_list = single_details['odList'][0]
            self.assertEqual(od_list['detailStatus'], 1)
            self.assertEqual(od_list['amount'], self.lottery_details['denomination'])
            self.assertIsNotNone(od_list['stationNumber'])
            self.station_number = od_list['stationNumber']  # 获取刮票工位
            self.assertIsNotNone(od_list['ticketNo'])
            self.assertEqual(od_list['bonusStatus'], 1)
            self.assertEqual(int(od_list['bonusAmount']), win_amount)
            self.assertIsNotNone(od_list['route'])

            self.assertIsNone(od_list['lotteryName'])
            self.assertIsNone(od_list['lotteryId'])
            self.assertIsNone(od_list['lottery'])
            self.assertIsNone(od_list['isUpload'])

            # 我得单买记录列表---中大奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 3})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result), 0)

            # 我得单买记录列表---未中奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 1})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result),0)


            # 单买订单信息---中小奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 2})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 1)

            self.assertEqual(len(my_single_order_result), 1)
            self.assertEqual(my_single_order_result[0]['buyType'], 0)
            self.assertEqual(int(my_single_order_result[0]['amount']), int(self.lottery_details['denomination']) * num)
            self.assertLessEqual(int(time.time()) - int(my_single_order_result[0]['createTime']), 15)
            self.assertEqual(my_single_order_result[0]['num'], num)
            self.assertIsNotNone(my_single_order_result[0]['orderNo'])
            self.assertEqual(int(my_single_order_result[0]['actualBonus']), win_amount * num)
            self.assertEqual(my_single_order_result[0]['bonusStatus'], 2)
            self.assertEqual(my_single_order_result[0]['bonus'], 1)
            self.assertEqual(my_single_order_result[0]['maxBonus'], self.lottery_details['max_bonus'])
            self.assertEqual(my_single_order_result[0]['orderStatus'], 2)
            self.assertEqual(my_single_order_result[0]['denomination'], self.lottery_details['denomination'])
            self.assertEqual(my_single_order_result[0]['lotteryName'], self.lottery_details['lottery_name'])

            # 单买订单信息---中大奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 3})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 0)

            # 单买订单信息---未中奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 1})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result),0)

            # 单买记录详情----------------------------------------------------------------------
            my_single_lottery_api = MySingleLotApi()
            my_single_lottery_api.get({'detailStatus': 1, 'orderNo': order_no, 'bonusStatus': 1})

            self.assertEqual(my_single_lottery_api.get_resp_code(), 200)

            my_single_lottery_result = my_single_lottery_api.get_resp_result()

            for x in my_single_lottery_result:
                self.assertEqual(x['detailStatus'], 1)
                self.assertEqual(int(x['amount']), int(self.lottery_details['denomination']))
                self.assertEqual(x['bonusStatus'], 1)
                self.assertEqual(int(x['bonusAmount']), win_amount)
                self.assertNotEqual(x['bonusTime'], x['createTime'])
                self.assertIsNotNone(x['ticketNo'])
                self.assertIsNotNone(x['route'])
                self.assertEqual(x['isUpload'], 1)
                self.assertIsNotNone(x['stationNumber'])
                self.assertEqual(int(x['lotteryId']), int(self.lottery_id))
                self.assertIsNone(x['lotteryName'], 1)
                lottery = x['lottery']
                self.assertEqual(lottery['lotteryName'], self.lottery_details['lottery_name'])
                self.assertEqual(lottery['denomination'], self.lottery_details['denomination'])
                self.assertEqual(lottery['maxReceiveNums'], self.lottery_details['max_receive_nums'])
                self.assertEqual(lottery['maxBonus'], self.lottery_details['max_bonus'])
                self.assertEqual(lottery['provinceId'], self.lottery_details['province_id'])
                self.assertEqual(lottery['salesStatus'], self.lottery_details['sales_status'])
                self.assertIsNone(lottery['abbr'])
                self.assertIsNone(lottery['name'])
                self.assertIsNone(lottery['stock'])
                self.assertIsNone(lottery['imgUrl'])

            # 获取今日彩种销量榜数据
            today_sales_api = TodaySalesApi()
            today_sales_api.get({'roomId': self.room_id, 'source': self.source})

            self.assertEqual(today_sales_api.get_resp_code(), 200)
            result = today_sales_api.get_resp_result()
            if self.lottery_details['lottery_name'] in str(result):
                for x in result:
                    if x['lotteryName'] == self.lottery_details['lottery_name']:
                        sales_after_bet = x['sales']
                        big_award_after = x['bigAward']

                        if flag == False:
                            self.assertEqual(int(sales_after_bet), num)
                            self.assertEqual(int(big_award_after), 0)
                        else:
                            self.assertEqual(int(sales_after_bet) - int(sales_before_bet), num)
                            self.assertEqual(big_award_after, big_award_before)
            else:
                self.assertTrue(False, msg='今日彩种销量榜未出现该彩种！')

            # 校验用户账户资金
            get_online_api = GetOnlineApi()
            get_online_api.get({'roomId':self.room_id})
            self.assertEqual(get_online_api.get_resp_code(), 200)

            result = get_online_api.get_resp_result()
            account = result['account']
            balance = None
            purchase_gold = None
            for x in account:
                if x['accountType'] == 1:
                    balance = x['balance']
                if x['accountType'] == 2:
                    purchase_gold = x['balance']
            self.assertEqual(int(purchase_gold), 0)
            self.assertEqual(int(balance), win_amount * num)

        elif win_amount >= 10000:

            # 我得单买记录列表---中小奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 2})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result),0)

            # 我得单买记录列表---中大奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 3})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result), 1)

            single_details = my_single_result[0]

            self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))
            self.assertEqual(single_details['userId'], self.user_id)
            self.assertEqual(single_details['userName'], MysqlHelper().get_user_details()['user_name'])
            self.assertEqual(single_details['lotteryName'], self.lottery_details['lottery_name'])
            self.assertEqual(single_details['buyType'], 0)
            self.assertEqual(single_details['orderStatus'], 2)
            self.assertEqual(single_details['num'], 1)
            self.assertEqual(int(single_details['amount']), self.lottery_details['denomination'])
            self.assertEqual(int(single_details['source']), int(self.source))
            self.assertEqual(int(single_details['roomId']), int(self.room_id))
            self.assertIsNotNone(single_details['window'])
            self.assertIsNotNone(single_details['stationNum'])
            self.assertEqual(int(single_details['bonusAmount']), win_amount)
            self.assertEqual(single_details['bonus'], 2)
            self.assertEqual(single_details['bonusStatus'], 3)

            self.assertIsNone(single_details['startTime'])
            self.assertIsNone(single_details['endTime'])
            self.assertIsNone(single_details['backAmount'])
            self.assertEqual(int(single_details['actualBonus']), win_amount)
            self.assertEqual(int(single_details['bonusAmount']), win_amount)
            self.assertIsNone(single_details['projectId'])
            self.assertIsNone(single_details['refund'])
            self.assertEqual(single_details['bonus'], 2)
            self.assertIsNone(single_details['bak'])
            self.assertIsNone(single_details['nikeName'])
            self.assertIsNone(single_details['headlogo'])
            self.assertIsNone(single_details['name'])
            self.assertIsNone(single_details['openId'])
            self.assertIsNone(single_details['drawType'])
            self.assertIsNone(single_details['memberNum'])
            self.assertIsNone(single_details['outTradeNo'])
            self.assertIsNone(single_details['ticketNo'])
            self.assertIsNotNone(single_details['orderNo'])
            self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))

            od_list = single_details['odList'][0]
            self.assertEqual(od_list['detailStatus'], 1)
            self.assertEqual(od_list['amount'], self.lottery_details['denomination'])
            self.assertIsNotNone(od_list['stationNumber'])
            self.station_number = od_list['stationNumber']  # 获取刮票工位
            self.assertIsNotNone(od_list['ticketNo'])
            self.assertEqual(od_list['bonusStatus'], 2)
            self.assertEqual(int(od_list['bonusAmount']), win_amount)
            self.assertIsNotNone(od_list['route'])

            self.assertIsNone(od_list['lotteryName'])
            self.assertIsNone(od_list['lotteryId'])
            self.assertIsNone(od_list['lottery'])
            self.assertIsNone(od_list['isUpload'])

            # 我得单买记录列表---未中奖
            my_single_api = MySingleApi()
            my_single_api.get({'status': 1})

            self.assertEqual(my_single_api.get_resp_code(), 200)
            my_single_result = my_single_api.get_resp_result()
            self.assertEqual(len(my_single_result), 0)

            # 单买订单信息---中小奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 2})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result),0)

            # 单买订单信息---中大奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 3})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 1)

            self.assertEqual(len(my_single_order_result), 1)
            self.assertEqual(my_single_order_result[0]['buyType'], 0)
            self.assertEqual(my_single_order_result[0]['amount'], self.lottery_details['denomination'])
            self.assertLessEqual(int(time.time()) - int(my_single_order_result[0]['createTime']), 15)
            self.assertEqual(my_single_order_result[0]['num'], 1)
            self.assertIsNotNone(my_single_order_result[0]['orderNo'])
            self.assertEqual(int(my_single_order_result[0]['actualBonus']), win_amount)
            self.assertEqual(my_single_order_result[0]['bonusStatus'], 3)
            self.assertEqual(my_single_order_result[0]['bonus'], 2)
            self.assertEqual(my_single_order_result[0]['maxBonus'], self.lottery_details['max_bonus'])
            self.assertEqual(my_single_order_result[0]['orderStatus'], 2)
            self.assertEqual(my_single_order_result[0]['denomination'], self.lottery_details['denomination'])
            self.assertEqual(my_single_order_result[0]['lotteryName'], self.lottery_details['lottery_name'])

            # 单买订单信息---未中奖
            my_single_order_api = MySingleOrderApi()
            my_single_order_api.get({'status': 1})
            self.assertEqual(my_single_order_api.get_resp_code(), 200)

            my_single_order_result = my_single_order_api.get_resp_result()
            self.assertEqual(len(my_single_order_result), 0)

            # 单买记录详情----------------------------------------------------------------------
            my_single_lottery_api = MySingleLotApi()
            my_single_lottery_api.get({'detailStatus': 1, 'orderNo': order_no, 'bonusStatus': 1})

            self.assertEqual(my_single_lottery_api.get_resp_code(), 200)

            my_single_lottery_result = my_single_lottery_api.get_resp_result()[0]

            self.assertEqual(my_single_lottery_result['detailStatus'], 1)
            self.assertEqual(my_single_lottery_result['amount'], self.lottery_details['denomination'])
            self.assertEqual(my_single_lottery_result['bonusStatus'], 2)
            self.assertEqual(int(my_single_lottery_result['bonusAmount']), win_amount)
            self.assertNotEqual(my_single_lottery_result['bonusTime'], my_single_lottery_result['createTime'])
            self.assertIsNotNone(my_single_lottery_result['ticketNo'])
            self.assertIsNotNone(my_single_lottery_result['route'])
            self.assertEqual(my_single_lottery_result['isUpload'], 1)
            self.assertIsNotNone(my_single_lottery_result['stationNumber'])
            self.assertEqual(int(my_single_lottery_result['lotteryId']), int(self.lottery_id))
            self.assertIsNone(my_single_lottery_result['lotteryName'], 1)
            lottery = my_single_lottery_result['lottery']
            self.assertEqual(lottery['lotteryName'], self.lottery_details['lottery_name'])
            self.assertEqual(lottery['denomination'], self.lottery_details['denomination'])
            self.assertEqual(lottery['maxReceiveNums'], self.lottery_details['max_receive_nums'])
            self.assertEqual(lottery['maxBonus'], self.lottery_details['max_bonus'])
            self.assertEqual(lottery['provinceId'], self.lottery_details['province_id'])
            self.assertEqual(lottery['salesStatus'], self.lottery_details['sales_status'])
            self.assertIsNone(lottery['abbr'])
            self.assertIsNone(lottery['name'])
            self.assertIsNone(lottery['stock'])
            self.assertIsNone(lottery['imgUrl'])

            # 获取今日彩种销量榜数据
            today_sales_api = TodaySalesApi()
            today_sales_api.get({'roomId': self.room_id, 'source': self.source})

            self.assertEqual(today_sales_api.get_resp_code(), 200)
            result = today_sales_api.get_resp_result()
            if self.lottery_details['lottery_name'] in str(result):
                for x in result:
                    if x['lotteryName'] == self.lottery_details['lottery_name']:
                        sales_after_bet = x['sales']
                        big_award_after = x['bigAward']

                        if flag == False:
                            self.assertEqual(int(sales_after_bet), num)
                            self.assertEqual(int(big_award_after), 1)
                        else:
                            self.assertEqual(int(sales_after_bet) - int(sales_before_bet), num)
                            self.assertEqual(int(big_award_after) - int(big_award_before),num)
            else:
                self.assertTrue(False, msg='今日彩种销量榜未出现该彩种！')

            # 校验用户账户资金
            get_online_api = GetOnlineApi()
            get_online_api.get({'roomId':self.room_id})
            self.assertEqual(get_online_api.get_resp_code(), 200)

            result = get_online_api.get_resp_result()
            account = result['account']
            balance = None
            purchase_gold = None
            for x in account:
                if x['accountType'] == 1:
                    balance = x['balance']
                if x['accountType'] == 2:
                    purchase_gold = x['balance']
            self.assertEqual(int(purchase_gold), 0)
            self.assertEqual(int(balance), 0)

        # 单买等待队列
        wait_rich_api = WaitRichApi()
        wait_rich_api.get({'roomId': self.room_id})
        self.assertEqual(wait_rich_api.get_resp_code(), 200)

        result = wait_rich_api.get_resp_result()
        self.assertNotIn(self.nickname,str(result))

    def test_bet_not_authentication(self):
        """
        测试购买未进行实名认证
        :return:
        """
        union_id = '70' + str(random.randint(1111111, 9999999))
        nickname = 'ceshi120001'
        head_pic = settings.TEST_HEAD_PIC
        bet_api = BetApi(union_id,nickname=nickname,head_pic=head_pic,source=1)
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 1, "buyType": 0, "window": 0, "roomId": self.room_id, "shareMethod": None,
             "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 417)
        self.assertEqual(bet_api.get_resp_message(), u"没实名认证的用户，不能下单")

    def test_single_one_not_win(self):
        """
        测试单买一张彩票未中奖流程
        :return:
        """
        test_data = {'nums':1,'win_amount':0}
        self.action(**test_data)

    def test_single_one_win_30(self):
        """
        测试单买一张彩票中小奖30元流程
        :return:
        """
        test_data = {'nums':1,'win_amount':30}
        self.action(**test_data)

    def test_single_one_win_30_num(self):
        """
        测试单买3张彩票中小奖30元流程
        :return:
        """
        test_data = {'nums':3,'win_amount':30}
        self.action(**test_data)

    def test_single_one_win_10000(self):
        """
        测试单买一张彩票中大奖10000元流程
        :return:
        """
        test_data = {'nums':1,'win_amount':10000}
        self.action(**test_data)

    def test_bet_low_stocks(self):
        """
        测试库存不足情况下代购30张
        :return:
        """
        Redis().fix_stock_day_cache(lottery_id=self.lottery_id, num=10)
        bet_api = BetApi()
        bet_api.get({"lotoId": self.lottery_id, "nums": 30, "buyType": 0, "window": 0, "roomId":self.room_id,'source':self.source ,
                     "shareMethod": None, "memberNum": None, 'provinceId': None})
        self.assertEqual(bet_api.get_resp_code(), 410)
        self.assertEqual(bet_api.get_resp_message(), u"库存不足")

    def test_bet_low_money(self):
        """
        测试余额不足情况下代购30张
        :return:
        """
        MysqlHelper().fix_user_money(balance=10)
        bet_api = BetApi()
        bet_api.get({"lotoId": self.lottery_id, "nums": 30, "buyType": 0, "window": 0, "roomId": self.room_id,'source':self.source,
                     "shareMethod": None,"memberNum": None, 'provinceId': None})
        self.assertEqual(bet_api.get_resp_code(), 408)
        self.assertEqual(bet_api.get_resp_message(), u"余额不足")

    def test_bet_regional_discrepancy(self):
        """
        测试北京用户不能购买彩票
        :return:
        """
        bet_api = BetApi()
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 1, "buyType": 0, "window": 2, "roomId": self.room_id, "shareMethod": None,
             "memberNum": None, 'provinceId': 11,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"地域不符")

    def test_bet_loto_id_null(self):
        """
        测试请求接口彩种id为空
        :return:
        """
        bet_api = BetApi()
        bet_api.get({"lotoId": None, "nums": 1, "buyType": 0, "window": 2, "roomId": self.room_id, "shareMethod": None,
                     "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"无此彩种")

    def test_bet_loto_id_error(self):
        """
        测试请求接口彩种id不存在
        :return:
        """
        bet_api = BetApi()
        bet_api.get({"lotoId": 9999, "nums": 1, "buyType": 0, "window": 2, "roomId": self.room_id, "shareMethod": None,
                     "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"无此彩种")

    def test_bet_nums_null(self):
        """
        测试请求购买数量为空
        :return:
        """
        bet_api = BetApi(self.union_id)
        bet_api.get({"lotoId": self.lottery_id, "nums": None, "buyType": 0, "window": 2, "roomId": self.room_id, "shareMethod": None,
                     "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"购买张数必须大于零")

    def test_bet_buy_type_null(self):
        """
        测试请求接口购买类型为空
        :return:
        """
        bet_api = BetApi(self.union_id)
        bet_api.get({"lotoId": self.lottery_id, "nums": 1, "buyType": None, "window": 2, "roomId": self.room_id, "shareMethod": None,
                     "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"不支持的购买方式")

    def test_bet_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        bet_api = BetApi(self.union_id)
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 1, "buyType": 0, "window": None, "roomId": None, "shareMethod": None,
             "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"房间不能为空")

    def test_bet_room_id_error(self):
        """
        测试请求接口房间ID不存在
        :return:
        """
        bet_api = BetApi(self.union_id)
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 1, "buyType": 0, "window": None, "roomId": 123123, "shareMethod": None,
             "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"房间不存在")

    def test_bet_share_method_null(self):
        """
        测试请求接口合买类型为空
        :return:
        """
        bet_api = BetApi(self.union_id)
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 15, "buyType": 1, "window": None, "roomId": self.room_id, "shareMethod": None,
             "memberNum": 2, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"分配方式不能为空")

    def test_bet_member_num_null(self):
        """
        测试请求接口合买人数为空
        :return:
        """
        bet_api = BetApi(self.union_id)
        bet_api.get({"lotoId": self.lottery_id, "nums": 15, "buyType": 1, "window": None, "roomId": self.room_id, "shareMethod": 0,
                     "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 401)
        self.assertEqual(bet_api.get_resp_message(), u"合买人数不能为空")

    def test_bet_be_fast(self):
        """
        测试禁止下单过快
        :return:
        """
        MysqlHelper().fix_user_money(balance=60)
        bet_api = BetApi(self.union_id)
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 1, "buyType": 0, "window": 0, "roomId": self.room_id, "shareMethod": None,
             "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 200)
        self.assertEqual(bet_api.get_resp_message(), u"下单成功")
        bet_api = BetApi(self.union_id)
        bet_api.get(
            {"lotoId": self.lottery_id, "nums": 1, "buyType": 0, "window": 0, "roomId": self.room_id, "shareMethod": None,
             "memberNum": None, 'provinceId': None,'source':self.source})
        self.assertEqual(bet_api.get_resp_code(), 411)
        self.assertEqual(bet_api.get_resp_message(), u"下单过快")

    def test_single_use_purchase_first(self):
        """
        测试购彩时优先扣除购彩金
        :return:
        """
        flag = None
        num = 1
        win_amount = 30
        detail_id = []
        MysqlHelper().fix_user_money(balance=self.lottery_amount * num,type = 3)
        bet_numbers = Redis().get_stock_day_cache(lottery_id=self.lottery_id)  # 下单前获取彩种库存
        time.sleep(0.3)

        today_sales_api = TodaySalesApi()
        today_sales_api.get({'roomId': self.room_id, 'source': self.source})

        self.assertEqual(today_sales_api.get_resp_code(), 200)
        result = today_sales_api.get_resp_result()
        sales_before_bet = None
        big_award_before = None
        if self.lottery_details['lottery_name'] in str(result):
            for x in result:
                if x['lotteryName'] == self.lottery_details['lottery_name']:
                    sales_before_bet = x['sales']
                    img_url = x['imGurl']

                    response = requests.get(url=img_url)
                    self.assertEqual(response.status_code, 200)
                    big_award_before = x['bigAward']
        else:
            flag = False

        # 下单 ----------------------------------------------------------------------
        bet_api = BetApi()
        bet_api.get({"lotoId": self.lottery_id, "nums": num, "buyType": 0, "window": 0, "shareMethod": None,
                     "memberNum": None, 'provinceId': None, 'roomId': self.room_id, 'source': self.source})
        self.assertEqual(bet_api.get_resp_code(), 200)
        self.assertEqual(bet_api.get_resp_message(), u"下单成功")

        after_bet_numbers = Redis().get_stock_day_cache(lottery_id=self.lottery_id)  # 下单成功后获取彩种库存
        self.assertEqual(int(bet_numbers) - int(after_bet_numbers), num)
        time.sleep(3)

        order_detail = MysqlHelper().get_order_detail(user_id=self.user_id)
        if order_detail['window'] == None and order_detail['station_num'] == None:

            # 单买等待队列
            wait_rich_api = WaitRichApi()
            wait_rich_api.get({'roomId': self.room_id})
            self.assertEqual(wait_rich_api.get_resp_code(), 200)

            result = wait_rich_api.get_resp_result()
            if self.nickname in str(result):
                for x in result:
                    if x['nickname'] == self.nickname:
                        self.assertEqual(x['num'], num)
                        self.assertEqual(x['window'], 0)
                        self.assertEqual(x['orderStatus'], 0)
            else:
                self.assertTrue(False, msg='单买待开奖区无该用户数据！')

            self.assertFalse(True, msg='没有空闲的窗口或工位！')
        else:
            self.station_number = order_detail['station_num']

        # 获取窗口状态----------------------------------------------------------------------
        count = 1
        max_count = 20
        while count < max_count:
            window_status_api = WindowStatusApi()
            window_status_api.get({'id': settings.DW_ROOM_ID, 'platformId': 1})

            self.assertEqual(window_status_api.get_resp_code(), 200)
            window_status_result = window_status_api.get_resp_result()

            window_nickname_list = [x['nickName'] for x in window_status_result]
            if settings.TEST_NICKNAME in window_nickname_list:

                for x in window_status_result:
                    if x['nickName'] == settings.TEST_NICKNAME:
                        self.window_id = x['num']
                        self.assertEqual(x['headPic'], settings.TEST_HEAD_PIC)
                        self.assertEqual(x['buyType'], 0)
                        self.assertEqual(x['lotName'], self.lottery_details['lottery_name'])
                        self.assertEqual(int(x['roomId']), int(settings.DW_ROOM_ID))
                        self.assertEqual(x['window_level'], 1)
                        self.assertEqual(x['label'], '单')
                        self.assertEqual(x['status'], '4')
                        self.assertIsNotNone(x['cameraUrl'])
                break
            else:
                time.sleep(1)
                count += 1
        self.assertLess(count, max_count)

        # 校验用户账户资金
        get_online_api = GetOnlineApi()
        get_online_api.get()
        self.assertEqual(get_online_api.get_resp_code(), 200)

        result = get_online_api.get_resp_result()
        account = result['account']
        balance = None
        purchase_gold = None
        for x in account:
            if x['accountType'] == 1:
                balance = x['balance']
            if x['accountType'] == 2:
                purchase_gold = x['balance']
        self.assertEqual(int(purchase_gold), 0)
        self.assertEqual(int(balance), self.lottery_amount * num)

        # 单买等待队列
        wait_rich_api = WaitRichApi()
        wait_rich_api.get({'roomId': self.room_id})
        self.assertEqual(wait_rich_api.get_resp_code(), 200)

        result = wait_rich_api.get_resp_result()
        if self.nickname in str(result):
            for x in result:
                if x['nickname'] == self.nickname:
                    self.assertEqual(x['num'], num)
                    self.assertNotEqual(x['window'], 0)
                    self.assertEqual(x['orderStatus'], 1)
        else:
            self.assertTrue(False, msg='单买待开奖区无该用户数据！')

        # 我得单买记录列表---待开奖----------------------------------------------------------------------
        my_single_api = MySingleApi()
        my_single_api.get({'status': 0})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 1)

        single_details = my_single_result[0]

        self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))
        self.assertEqual(single_details['userId'], self.user_id)
        self.assertEqual(single_details['userName'], MysqlHelper().get_user_details()['user_name'])
        self.assertEqual(single_details['lotteryName'], self.lottery_details['lottery_name'])
        self.assertEqual(single_details['buyType'], 0)
        self.assertEqual(single_details['orderStatus'], 1)
        self.assertEqual(single_details['num'], num)
        self.assertEqual(int(single_details['amount']), int(self.lottery_details['denomination']) * num)
        self.assertEqual(int(single_details['source']), int(self.source))
        self.assertEqual(int(single_details['roomId']), int(self.room_id))
        self.assertIsNotNone(single_details['window'])
        self.assertIsNotNone(single_details['stationNum'])
        self.assertIsNone(single_details['bonusAmount'])
        self.assertIsNone(single_details['bonus'])
        self.assertIsNone(single_details['bonusStatus'])

        self.assertIsNone(single_details['startTime'])
        self.assertIsNone(single_details['endTime'])
        self.assertIsNone(single_details['backAmount'])
        self.assertIsNone(single_details['actualBonus'])
        self.assertIsNone(single_details['bonusAmount'])
        self.assertIsNone(single_details['projectId'])
        self.assertIsNone(single_details['refund'])
        self.assertIsNone(single_details['bonus'])
        self.assertIsNone(single_details['bak'])
        self.assertIsNone(single_details['nikeName'])
        self.assertIsNone(single_details['headlogo'])
        self.assertIsNone(single_details['name'])
        self.assertIsNone(single_details['openId'])
        self.assertIsNone(single_details['drawType'])
        self.assertIsNone(single_details['memberNum'])
        self.assertIsNone(single_details['outTradeNo'])
        self.assertIsNone(single_details['ticketNo'])
        self.assertIsNotNone(single_details['orderNo'])
        self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))

        od_list = single_details['odList']
        for x in od_list:
            self.assertEqual(x['detailStatus'], 0)
            self.assertEqual(x['amount'], self.lottery_details['denomination'])
            self.assertEqual(x['stationNumber'], self.station_number)
            self.assertIsNone(x['ticketNo'])
            self.assertIsNone(x['bonusStatus'])
            self.assertIsNone(x['bonusAmount'])
            self.assertIsNone(x['route'])

            self.assertIsNone(x['lotteryName'])
            self.assertIsNone(x['lotteryId'])
            self.assertIsNone(x['lottery'])
            self.assertIsNone(x['isUpload'])

            detail_id.append(x['id'])

        # 我得单买记录列表---未中奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 1})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 0)

        # 我得单买记录列表---中小奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 2})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 0)

        # 我得单买记录列表---中大奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 3})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 0)

        # 单买订单信息---待开奖----------------------------------------------------------------------
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 0})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 1)
        self.assertEqual(my_single_order_result[0]['buyType'], 0)
        self.assertEqual(int(my_single_order_result[0]['amount']), int(self.lottery_details['denomination']) * num)
        self.assertEqual(my_single_order_result[0]['num'], num)
        self.assertEqual(my_single_order_result[0]['orderStatus'], 1)
        self.assertEqual(my_single_order_result[0]['denomination'], self.lottery_details['denomination'])
        self.assertEqual(my_single_order_result[0]['lotteryName'], self.lottery_details['lottery_name'])
        self.assertEqual(my_single_order_result[0]['maxBonus'], self.lottery_details['max_bonus'])

        self.assertLessEqual(int(time.time()) - int(my_single_order_result[0]['createTime']), 15)
        self.assertIsNotNone(my_single_order_result[0]['orderNo'])

        order_no = my_single_order_result[0]['orderNo']

        # 单买订单信息---未中奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 1})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买订单信息---中小奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 2})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买订单信息---中大奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 3})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买记录详情----------------------------------------------------------------------
        my_single_lottery_api = MySingleLotApi()
        my_single_lottery_api.get({'detailStatus': 0, 'orderNo': None, 'bonusStatus': None})

        self.assertEqual(my_single_lottery_api.get_resp_code(), 200)

        my_single_lottery_result = my_single_lottery_api.get_resp_result()
        self.assertEqual(len(my_single_lottery_result), num)

        result = my_single_lottery_result[0]
        self.assertEqual(result['detailStatus'], 0)
        self.assertEqual(result['amount'], self.lottery_amount)
        self.assertIsNone(result['bonusStatus'])
        self.assertIsNone(result['bonusAmount'])
        self.assertIsNone(result['bonusTime'])
        self.assertIsNone(result['ticketNo'])
        self.assertIsNone(result['route'])
        self.assertEqual(result['isUpload'], 0)
        self.assertIsNotNone(result['stationNumber'])

        lottery = result['lottery']
        self.assertEqual(lottery['lotteryName'], self.lottery_details['lottery_name'])
        self.assertEqual(lottery['denomination'], self.lottery_details['denomination'])
        self.assertEqual(lottery['maxReceiveNums'], self.lottery_details['max_receive_nums'])
        self.assertEqual(lottery['maxBonus'], self.lottery_details['max_bonus'])
        self.assertEqual(lottery['provinceId'], self.lottery_details['province_id'])
        self.assertEqual(lottery['salesStatus'], self.lottery_details['sales_status'])
        self.assertIsNone(lottery['abbr'])
        self.assertIsNone(lottery['name'])
        self.assertIsNone(lottery['stock'])
        self.assertIsNone(lottery['imgUrl'])

        # 用户账户记录----------------------------------------------------------------------
        my_ac_det_api = MyAcDetApi()
        my_ac_det_api.get({'unionId': self.union_id, 'source': 1})

        self.assertEqual(my_ac_det_api.get_resp_code(), 200)
        self.assertEqual(my_ac_det_api.get_resp_message(), u'success')

        result = my_ac_det_api.get_resp_result()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['user_id'], MysqlHelper().get_user_details()['id'])
        self.assertEqual(result[0]['tradeType'], 2)
        self.assertEqual(str(result[0]['amountS']), '-{0}.0'.format(int(self.lottery_details['denomination']) * num))

        # 开奖---未中奖----------------------------------------------------------------------*****************************

        for x in detail_id:
            send_prize(detail_id=x, win_amount=win_amount)
            time.sleep(7)  # 开奖预留时间

        # 开奖后获取当前窗口状态----------------------------------------------------------------------
        window_status_api = WindowStatusApi()
        window_status_api.get({'id': settings.DW_ROOM_ID, 'platformId': 1})

        self.assertEqual(window_status_api.get_resp_code(), 200)
        window_status_result = window_status_api.get_resp_result()

        window_nickname_list = [x['nickName'] for x in window_status_result]

        self.assertNotIn(settings.TEST_NICKNAME, window_nickname_list)

        # 我得单买记录列表---待开奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 0})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 0)

        # 单买订单信息---待开奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 0})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 我得单买记录列表---中小奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 2})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 1)

        single_details = my_single_result[0]

        self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))
        self.assertEqual(single_details['userId'], self.user_id)
        self.assertEqual(single_details['userName'], MysqlHelper().get_user_details()['user_name'])
        self.assertEqual(single_details['lotteryName'], self.lottery_details['lottery_name'])
        self.assertEqual(single_details['buyType'], 0)
        self.assertEqual(single_details['orderStatus'], 2)
        self.assertEqual(single_details['num'], num)
        self.assertEqual(int(single_details['amount']), int(self.lottery_details['denomination']) * num)
        self.assertEqual(int(single_details['source']), int(self.source))
        self.assertEqual(int(single_details['roomId']), int(self.room_id))
        self.assertIsNotNone(single_details['window'])
        self.assertIsNotNone(single_details['stationNum'])
        self.assertEqual(int(single_details['bonusAmount']), win_amount * num)
        self.assertEqual(single_details['bonus'], 1)
        self.assertEqual(single_details['bonusStatus'], 2)

        self.assertIsNone(single_details['startTime'])
        self.assertIsNone(single_details['endTime'])
        self.assertIsNone(single_details['backAmount'])
        self.assertEqual(int(single_details['actualBonus']), win_amount * num)
        self.assertEqual(int(single_details['bonusAmount']), win_amount * num)
        self.assertIsNone(single_details['projectId'])
        self.assertIsNone(single_details['refund'])
        self.assertEqual(single_details['bonus'], 1)
        self.assertIsNone(single_details['bak'])
        self.assertIsNone(single_details['nikeName'])
        self.assertIsNone(single_details['headlogo'])
        self.assertIsNone(single_details['name'])
        self.assertIsNone(single_details['openId'])
        self.assertIsNone(single_details['drawType'])
        self.assertIsNone(single_details['memberNum'])
        self.assertIsNone(single_details['outTradeNo'])
        self.assertIsNone(single_details['ticketNo'])
        self.assertIsNotNone(single_details['orderNo'])
        self.assertEqual(int(single_details['lotteryId']), int(self.lottery_id))

        od_list = single_details['odList'][0]
        self.assertEqual(od_list['detailStatus'], 1)
        self.assertEqual(od_list['amount'], self.lottery_details['denomination'])
        self.assertIsNotNone(od_list['stationNumber'])
        self.station_number = od_list['stationNumber']  # 获取刮票工位
        self.assertIsNotNone(od_list['ticketNo'])
        self.assertEqual(od_list['bonusStatus'], 1)
        self.assertEqual(int(od_list['bonusAmount']), win_amount)
        self.assertIsNotNone(od_list['route'])

        self.assertIsNone(od_list['lotteryName'])
        self.assertIsNone(od_list['lotteryId'])
        self.assertIsNone(od_list['lottery'])
        self.assertIsNone(od_list['isUpload'])

        # 我得单买记录列表---中大奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 3})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 0)

        # 我得单买记录列表---未中奖
        my_single_api = MySingleApi()
        my_single_api.get({'status': 1})

        self.assertEqual(my_single_api.get_resp_code(), 200)
        my_single_result = my_single_api.get_resp_result()
        self.assertEqual(len(my_single_result), 0)

        # 单买订单信息---中小奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 2})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 1)

        self.assertEqual(len(my_single_order_result), 1)
        self.assertEqual(my_single_order_result[0]['buyType'], 0)
        self.assertEqual(int(my_single_order_result[0]['amount']), int(self.lottery_details['denomination']) * num)
        self.assertLessEqual(int(time.time()) - int(my_single_order_result[0]['createTime']), 15)
        self.assertEqual(my_single_order_result[0]['num'], num)
        self.assertIsNotNone(my_single_order_result[0]['orderNo'])
        self.assertEqual(int(my_single_order_result[0]['actualBonus']), win_amount * num)
        self.assertEqual(my_single_order_result[0]['bonusStatus'], 2)
        self.assertEqual(my_single_order_result[0]['bonus'], 1)
        self.assertEqual(my_single_order_result[0]['maxBonus'], self.lottery_details['max_bonus'])
        self.assertEqual(my_single_order_result[0]['orderStatus'], 2)
        self.assertEqual(my_single_order_result[0]['denomination'], self.lottery_details['denomination'])
        self.assertEqual(my_single_order_result[0]['lotteryName'], self.lottery_details['lottery_name'])

        # 单买订单信息---中大奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 3})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买订单信息---未中奖
        my_single_order_api = MySingleOrderApi()
        my_single_order_api.get({'status': 1})
        self.assertEqual(my_single_order_api.get_resp_code(), 200)

        my_single_order_result = my_single_order_api.get_resp_result()
        self.assertEqual(len(my_single_order_result), 0)

        # 单买记录详情----------------------------------------------------------------------
        my_single_lottery_api = MySingleLotApi()
        my_single_lottery_api.get({'detailStatus': 1, 'orderNo': order_no, 'bonusStatus': 1})

        self.assertEqual(my_single_lottery_api.get_resp_code(), 200)

        my_single_lottery_result = my_single_lottery_api.get_resp_result()

        for x in my_single_lottery_result:
            self.assertEqual(x['detailStatus'], 1)
            self.assertEqual(int(x['amount']), int(self.lottery_details['denomination']))
            self.assertEqual(x['bonusStatus'], 1)
            self.assertEqual(int(x['bonusAmount']), win_amount)
            self.assertNotEqual(x['bonusTime'], x['createTime'])
            self.assertIsNotNone(x['ticketNo'])
            self.assertIsNotNone(x['route'])
            self.assertEqual(x['isUpload'], 1)
            self.assertIsNotNone(x['stationNumber'])
            self.assertEqual(int(x['lotteryId']), int(self.lottery_id))
            self.assertIsNone(x['lotteryName'], 1)
            lottery = x['lottery']
            self.assertEqual(lottery['lotteryName'], self.lottery_details['lottery_name'])
            self.assertEqual(lottery['denomination'], self.lottery_details['denomination'])
            self.assertEqual(lottery['maxReceiveNums'], self.lottery_details['max_receive_nums'])
            self.assertEqual(lottery['maxBonus'], self.lottery_details['max_bonus'])
            self.assertEqual(lottery['provinceId'], self.lottery_details['province_id'])
            self.assertEqual(lottery['salesStatus'], self.lottery_details['sales_status'])
            self.assertIsNone(lottery['abbr'])
            self.assertIsNone(lottery['name'])
            self.assertIsNone(lottery['stock'])
            self.assertIsNone(lottery['imgUrl'])

        # 获取今日彩种销量榜数据
        today_sales_api = TodaySalesApi()
        today_sales_api.get({'roomId': self.room_id, 'source': self.source})

        self.assertEqual(today_sales_api.get_resp_code(), 200)
        result = today_sales_api.get_resp_result()
        if self.lottery_details['lottery_name'] in str(result):
            for x in result:
                if x['lotteryName'] == self.lottery_details['lottery_name']:
                    sales_after_bet = x['sales']
                    big_award_after = x['bigAward']

                    if flag == False:
                        self.assertEqual(int(sales_after_bet), num)
                        self.assertEqual(int(big_award_after), 0)
                    else:
                        self.assertEqual(int(sales_after_bet) - int(sales_before_bet), num)
                        self.assertEqual(big_award_after, big_award_before)
        else:
            self.assertTrue(False, msg='今日彩种销量榜未出现该彩种！')

        # 校验用户账户资金
        get_online_api = GetOnlineApi()
        get_online_api.get({'roomId': self.room_id})
        self.assertEqual(get_online_api.get_resp_code(), 200)

        result = get_online_api.get_resp_result()
        account = result['account']
        balance = None
        purchase_gold = None
        for x in account:
            if x['accountType'] == 1:
                balance = x['balance']
            if x['accountType'] == 2:
                purchase_gold = x['balance']
        self.assertEqual(int(purchase_gold), 0)
        self.assertEqual(int(balance), win_amount * num + self.lottery_amount * num)


    def tearDown(self):
        mysql = MysqlHelper()
        mysql.delete_lot_order(self.user_id)
        mysql.reset_station(self.station_number)
        mysql.reset_window(window_id=self.window_id,room_id=settings.DW_ROOM_ID)
        Redis().fix_stock_day_cache(lottery_id=self.lottery_id, num=9999)
        mysql.fix_user_money(balance=0)
        mysql.delete_account_details(self.user_id)
        time.sleep(2)
