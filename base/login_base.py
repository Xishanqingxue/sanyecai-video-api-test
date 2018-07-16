# -*- coding:utf-8 -*-
from base.base_log import BaseLogger
from base.base_api import BaseApi
from base.login import LoginApi
import requests

logger = BaseLogger(__name__).get_logger()


class LoginBaseApi(BaseApi):

    def get_token_id(self):
        """
        获取用户登录成功后token
        :return:
        """
        token_id = LoginApi().login(only_token=True)
        return token_id

    def get(self, data=None):
        """
        请求方式：GET
        :param data:
        :return:
        """
        request_data = self.format_param(data)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        token_id = self.get_token_id()
        s.cookies.set('VIDEO_LOTTERY_CODE_TOKEN_ID', token_id)
        self.response = s.get(url=self.api_url(), params=request_data, headers=self.headers)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
