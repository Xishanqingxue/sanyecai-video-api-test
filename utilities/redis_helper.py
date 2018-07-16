# -*- coding:utf-8 -*-
from base.base_redis import BaseRedis


class Redis(BaseRedis):


    def get_stock_day_cache(self,stock_id):
        """
        获取彩种库存
        :param id:
        :return:
        """
        numbers = self.get('stock_day_cache_{0}'.format(stock_id))
        return numbers

    def fix_stock_day_cache(self,stock_id,num):
        """
        修改彩种库存数量
        :param stock_id:
        :param num:
        :return:
        """
        self.set('stock_day_cache_{0}'.format(stock_id),num)

    def clean_user_info(self,token):
        """
        清除用户信息
        :param token:
        :return:
        """
        self.delete(token)

    def get_image_code(self,mobile):
        """
        获取图形验证码
        :param mobile:
        :return:
        """
        image_code = self.get('txyz{0}'.format(mobile))
        return image_code

    def get_sms_code(self,mobile,type):
        """
        获取短信验证码
        :param mobile:
        :param type:
        :return:
        """
        if type == 'rz':
            sms_code = self.get('rz_sms_code{0}'.format(mobile))
            return sms_code
        elif type == 'tx':
            sms_code = self.get('tx_sms_code{0}'.format(mobile))
            return sms_code
        elif type == 'tj':
            sms_code = self.get('tj_sms_code{0}'.format(mobile))
            return sms_code
        elif type == 'xg':
            sms_code = self.get('xg_sms_code{0}'.format(mobile))
            return sms_code

    def fix_send_sms_code_num(self,mobile,num):
        """
        修改当天已发送短信验证码次数
        :param mobile:
        :param num:
        :return:
        """
        self.set('rz_sms_num{0}'.format(mobile),num)

    def fix_user_withdraw_times(self,auth_id,num):
        """
        修改用户当天提现次数
        :param auth_id:
        :param num:
        :return:
        """
        self.set('tx_num{0}'.format(auth_id),num)

    def fix_user_withdraw_money_today(self,auth_id,money):
        """
        修改用户当天提现总数
        :param auth_id:
        :param money:
        :return:
        """
        self.set('tx_total_money{0}'.format(auth_id),money)