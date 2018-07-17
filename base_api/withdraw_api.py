# -*- coding:utf-8 -*-
from base.login_base import LoginBaseApi


class WithdrawApplyApi(LoginBaseApi):
    """
    提现申请
    """
    url = "/finan/withdrawalsApply"

    def build_custom_param(self, data):
        return {'amount': data['amount'], 'source': data['source'], 'mobile': data['mobile'],
                'verCode': data['verCode'], 'type': data['type'],'bindingId':data['bindingId']}
