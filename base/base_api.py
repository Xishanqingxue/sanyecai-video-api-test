# -*- coding:utf-8 -*-
from base.base_log import BaseLogger
import json
import requests
import settings


logger = BaseLogger(__name__).get_logger()

class BaseApi(object):
    url = ''
    base_url = settings.API_BASE_URL

    def __init__(self):
        self.response = None
        self.headers = settings.API_HEADERS

    def api_url(self):
        """
        拼接url
        :return:
        """
        url = "{0}{1}".format(self.base_url,self.url)
        logger.info('Test Url:{0}'.format(url))
        return url

    def build_base_param(self):
        """
        构建共有入参
        :return:
        """
        return {

        }

    def build_custom_param(self, data):
        """
        构建除共有参数外其余参数，接口封装时将该方法重写
        :param data:
        :return:
        """
        return {}

    def format_param(self,data):
        """
        合并共有参数和其他所需参数
        :param data:
        :return:
        """
        if not data:
            data = {}
        base_param = self.build_base_param()
        custom_param = self.build_custom_param(data)
        data.update(base_param)
        data.update(custom_param)
        logger.info('Param:{0}'.format(data))
        return data

    def get(self, data=None):
        """
        请求方式：GET
        :param data:
        :return:
        """
        request_data = self.format_param(data)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        self.response = s.get(url=self.api_url(), params=request_data, headers=self.headers)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
        return self.response

    def post(self, data=None):
        """
        请求方式：POST
        :param data:
        :return:
        """
        request_data = self.format_param(data)
        logger.info('Data:{0}'.format(request_data))
        s = requests.session()
        self.response = s.post(url=self.api_url(), params=request_data, headers=self.headers)
        logger.info('Headers:{0}'.format(self.response.request.headers))
        logger.info('Response:{0}'.format(self.response.text))
        return self.response

    def get_status_code(self):
        """
        返回请求状态码
        :return:
        """
        if self.response:
            return self.response.status_code

    def get_resp_code(self):
        """
        获取回参中状态码
        :return:
        """
        if self.response:
            return int(json.loads(self.response.text)['code'])

    def get_resp_message(self):
        """
        获取回参中消息
        :return:
        """
        if self.response:
            return json.loads(self.response.text)['message']

    def get_resp_result(self):
        """
        获取回参中result
        :return:
        """
        if self.response:
            return json.loads(self.response.text)['result']
