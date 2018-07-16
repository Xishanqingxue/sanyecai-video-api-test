# -*- coding:utf-8 -*-
import requests
from base.base_api import BaseApi
from base.base_log import BaseLogger
from base.base_helper import md5
import settings
import re

logger = BaseLogger(__name__).get_logger()


class LoginApi(BaseApi):
    """
    登录接口/创建彩票用户
    """
    url = '/login'

    def login(self, unionID=settings.TEST_UNION_ID, source=settings.TEST_SOURCE, nickname=settings.TEST_NICKNAME,
              head_pic=settings.TEST_HEAD_PIC, only_token=False):
        # 接口登录
        sign_text = "{0}_{1}_{2}_{3}67!@#$%^&*()_(&%$#!_)(*&^%$#@!rftgy2345678uhij".format(unionID, source,
                                                                                           nickname, head_pic)
        sign_format = md5(sign_text)
        data = {'unionId': unionID, 'source': source, 'nickname': nickname, 'sign': sign_format,
                'head_pic': head_pic, 'ip': '61.149.11.114', 'uv': 'web'}
        logger.info('Data:{0}'.format(data))
        self.response = requests.get(url=self.api_url(), params=data, headers=settings.API_HEADERS, verify=False)
        logger.info('Response:{0}'.format(self.response.content))
        if only_token:
            headers = self.response.headers
            token = re.findall(r"TOKEN_ID=(.+?);", str(headers))
            if len(token) == 1:
                return token[0]
            else:
                return None
        else:
            return self.response

    # def login(self, login_mobile=settings.TEST_USER_MOBILE, only_session_id=False):
    #     # H5页面彩票系统登录
    #     identity = DaWangLoginApi().login(login_name=login_mobile, only_get_identity=True)
    #     data = {'token': identity}
    #     self.response = requests.get(self.api_url(), params=data, headers=settings.API_HEADERS)
    #
    #     if not only_session_id:
    #         return self.response
    #     else:
    #         headers = self.response.headers
    #         session_id = re.findall(r"session_id=(.+?);", str(headers))
    #         if len(session_id) == 1:
    #             return session_id[0]
    #         else:
    #             return None
