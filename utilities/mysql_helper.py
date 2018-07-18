# -*- coding:utf-8 -*-
import base.base_mysql as base_mysql
import settings
from base.base_log import BaseLogger

# from base_api.my_single_lot_api import InfoMySingleLotApi

logger = BaseLogger(__name__).get_logger()


class MysqlHelper(object):

    # def get_single_query_list(self):
    #     """
    #     获取等待分配窗口信息用户列表
    #     :return:
    #     """
    #     single_list = base_mysql.execute('select distinct user_id from (select * from lot_order where project_id is null and '
    #                        '(order_status = 0 or order_status = 1)) t limit 0,5',is_fetchone=False)
    #     return single_list
    #
    # def get_user_info_nickname(self,user_id):
    #     """
    #     获取用户的nickname
    #     :param user_id:
    #     :return:
    #     """
    #     nickname = []
    #     for i in range(len(user_id)):
    #         nick_name_one = base_mysql.execute("select nickname from lot_user_info where id=%s",params=user_id[i]["user_id"])
    #         nickname.append(nick_name_one)
    #     return nickname

    # def delete_order_detail_use_order_id(self,union_id):
    #     """
    #     删除lot_order_detail中数据
    #     :param union_id:
    #     :return:
    #     """
    #     info_my_single = InfoMySingleLotApi(union_id)
    #     info_my_single.get({'unionId': union_id, 'source': 1, 'detailStatus': None,
    #                         'bonusStatus': None, 'page': 1, 'length': 20})
    #     result = info_my_single.get_resp_result()
    #     order_id = []
    #     for i in range(len(result)):
    #         order_id.append(result[i]['orderId'])
    #     for i in order_id:
    #         MysqlHelper().delete_order_details(i)

    def get_user_details(self, nickname=settings.TEST_NICKNAME):
        """
        获取用户信息
        :param union_id:
        :return:
        """
        details = base_mysql.execute('select * from lot_user_info where nickname=%s', params=(nickname))
        return details

    def delete_user(self, union_id):
        """
        删除用户信息
        :param union_id:
        :return:
        """
        try:
            user_id = base_mysql.execute('select id from lot_user_info where union_id=%s', params=(union_id))['id']
            base_mysql.execute('delete from lot_user_info where union_id=%s', params=(union_id))
            base_mysql.execute('delete from lot_account where user_id=%s', params=user_id)
        except:
            logger.error('Delete user failed!')

    def fix_stock_user(self,number=9999):
        """
        修改工位上的票数（全部的工位）
        :return:
        """
        base_mysql.execute('update lot_stock_user set stock_nums=%s',params=(number))

    def get_lottery_detail(self,id):
        """
        获取某ID的彩种信息
        :param id:
        :return:
        """
        one_lottery = base_mysql.execute('select * from lot_lottery where id=%s ',params=(id))
        return one_lottery

    def get_sell_lottery(self, room_id):
        """
        获取房间在售彩种
        :param room_id:
        :return:
        """
        lottery = base_mysql.execute('select * from lot_lottery_room where room_id=%s having status=1 order by sort_by',
                                     params=(room_id), is_fetchone=False)
        return lottery

    def fix_user_money(self, balance, nickname=settings.TEST_NICKNAME):
        """
        修改用户金额
        :param money:
        :return:
        """
        auth_id = base_mysql.execute('select auth_id from lot_user_info where nickname=%s', params=(nickname))
        base_mysql.execute('update lot_account set balance=%s where auth_id=%s', params=(balance, auth_id['auth_id']))

    def delete_lot_order(self, user_id):
        """
        删除订单
        :param user_id:
        :return:
        """
        try:
            order_id = base_mysql.execute('select id from lot_order where user_id=%s', params=(user_id))

            base_mysql.execute('delete from lot_order_detail where order_id=%s', params=(order_id['id']))

            base_mysql.execute('delete from lot_order where user_id=%s', params=(user_id))
        except Exception as e:
            logger.error(e)

    def get_order_id(self,user_id):
        """
        获取订单order_id
        :param user_id:
        :return:
        """
        order_id = base_mysql.execute('select id from lot_order where user_id=%s', params=(user_id))
        return order_id['id']

    def get_order_detail(self,user_id):
        """
        获取订单信息
        :param user_id:
        :return:
        """
        order_detail = base_mysql.execute('select * from lot_order where user_id=%s',params=(user_id))
        return order_detail


    def reset_station(self,station_num):
        """
        重置工位状态
        :param station_num:
        :return:
        """
        base_mysql.execute('update lot_station set station_status=3 where number=%s',params=(station_num))
        return self

    def get_station_status(self):
        """
        获取所有工位状态
        :return:
        """
        result = []
        status_list = base_mysql.execute('select station_status from lot_station',is_fetchone=False)
        for x in status_list:
            result.append(x['station_status'])
        return result

    def reset_window(self, window_id, room_id):
        """
        重置助理窗口
        :param window_id:
        :param room_id:
        :return:
        """
        if window_id == None:
            base_mysql.execute('update lot_live_window set status=3 where room_id=%s',params=(room_id))
        else:
            base_mysql.execute('update lot_live_window set status=3 where num=%s and room_id=%s',params=(window_id, room_id))
            logger.info('更新窗口状态成功')

    #
    # def get_lot_order(self,user_id):
    #     """
    #     获取订单
    #     :param user_id:
    #     :return:
    #     """
    #     order_list = base_mysql.execute('select * from lot_order where user_id=%s',params=(user_id),is_fetchone=False)
    #     return order_list
    #
    def get_distributed_order(self,user_id):
        """
        获取已派单订单
        :param user_id:
        :return:
        """
        details = base_mysql.execute('SELECT * FROM lot_order_detail WHERE detail_status=0 and station_number is NOT NULL HAVING order_id = (SELECT id FROM lot_order WHERE user_id=%s)',params=(user_id),is_fetchone=False)
        return details

    def delete_account_details(self, user_id):
        """
        删除用户消费记录
        :param user_id:
        :return:
        """
        base_mysql.execute('delete from lot_account_detail where user_id=%s', params=(user_id))

    def get_lot_account_info(self, user_id):
        """
        获取用户account信息
        :param union_id:
        :return:
        """
        account_info = base_mysql.execute('select * from lot_account where user_id = %s', params=(user_id))
        return account_info

    #
    def get_lot_user_info(self, id):
        """
        获取用户user_info信息
        :param id:
        :return:
        """
        user_info = base_mysql.execute('select * from lot_user_info where id = %s', params=(id))
        return user_info

    #
    #     def get_province_name(self,id):
    #         """
    #         获取省份的name
    #         :param id:
    #         :return:
    #         """
    #         province_name = base_mysql.execute("select name from lot_province where id=%s",params=id)
    #         return province_name
    #
    #     def get_order_details(self,order_id):
    #         """
    #         获取用户购彩记录
    #         :param order_id:
    #         :return:
    #         """
    #         all_list = base_mysql.execute("select * from lot_order_detail where order_id=%s",params=(order_id))
    #         return all_list
    #
    #     def delete_order_details(self,order_id):
    #         """
    #         删除用户的购彩记录
    #         :param order_id:
    #         :return:
    #         """
    #         base_mysql.execute("delete from lot_order_detail where order_id=%s",params=(order_id))
    #
    def delete_user_auth(self, card_no):
        """
        清除用户实名认证信息
        :param mobile:
        :return:
        """
        try:
            auth_id = base_mysql.execute('select id  from lot_user_auth where card_no=%s', params=(card_no))
            user_id = base_mysql.execute('select id from lot_user_info where auth_id=%s', params=(auth_id['id']))
            base_mysql.execute('delete from lot_user_auth where card_no=%s', params=(card_no))
            base_mysql.execute('update lot_user_info set auth_id="" WHERE id=%s', params=user_id['id'])
        except:
            pass

    #
    def get_bank_list(self):
        """
        获取银行列表
        :return:
        """
        bank_list = base_mysql.execute('select * from lot_bank', is_fetchone=False)
        return bank_list

    #
    def get_user_auth(self, auth_id):
        """
        获取用户lot_user_auth信息
        :param auth_id:
        :return:
        """
        auth = base_mysql.execute('select * from lot_user_auth where id=%s', params=(auth_id))
        return auth

    #
    def fix_user_mobile(self, auth_id, mobile):
        """
        修改用户的绑定手机号
        :param auth_id:
        :param mobile:
        :return:
        """
        base_mysql.execute('update lot_user_auth set mobile=%s where id=%s', params=(mobile, auth_id))

    #
    def delete_bind_card(self, auth_id):
        """
        删除用户绑卡信息
        :param auth_id:
        :return:
        """
        base_mysql.execute('delete from lot_user_binding where auth_id=%s', params=(auth_id))

    #
    def fix_user_withdraw_amount(self, auth_id, amount):
        """
        修改用户提现额度
        :param auth_id:
        :param amount:
        :return:
        """
        base_mysql.execute('update lot_user_auth set amount_of_cash=%s where id=%s', params=(amount, auth_id))

    #
    def delete_user_withdraw_log(self, auth_id):
        """
        删除用户提现记录
        :param auth_id:
        :return:
        """
        base_mysql.execute('delete from lot_present_record where auth_id=%s', params=(auth_id))

    #
    def send_prize_after(self, image_url, detail_id, is_upload=1):
        """
        手动开奖完成后，向数据库中写入中奖图片地址并标志为已上传
        :param image_url:
        :param detail_id:
        :return:
        """
        base_mysql.execute("update lot_order_detail set route=%s,is_upload=%s where id=%s",
                           params=(image_url, is_upload, detail_id))
