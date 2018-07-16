# -*- coding: UTF-8 -*-
import hashlib
import random
import re
import time
import settings
import json
import requests
from utilities.mysql_helper import MysqlHelper


def md5(string):
    """
    创建md5加密字符串
    :param string:
    :return:
    """
    m = hashlib.md5()
    m.update(string.encode(encoding='UTF-8'))
    return m.hexdigest()


def generate_random_nickname(words=5):
    """
    生成一个随机昵称，以“测试”开头，words参数指定昵称字数
    :param words:
    :return:
    """
    name = '测试'
    for x in range(words-2):
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xf9)
        val = f'{head:x}{body:x}'
        str = bytes.fromhex(val).decode('gb2312')
        name += str
    return name

def get_nums_in_string(string):
    """
    获取字符串中的数字，返回数组
    :param string:
    :return:
    """
    p = re.compile('\d+')
    nums = p.findall(string)
    return nums

def get_someone_in_string(string,a,b):
    """
    获取字符串中两个值之间的部分,参数类型均为string
    :param string,a,b:
    :return:
    """
    key = string  # 这段是你要匹配的文本
    p = "(?<=%s).+?(?=%s)" % (a,b) # 这是我们写的正则表达式规则
    pattern = re.compile(p)  # 编译这段正则表达式
    matcher = re.findall(pattern, key)  # 在源文本中搜索符合正则表达式的部分
    return matcher

def convert_to_timestamp(time_format):
    """
    转换为时间戳
    :param time_format:
    :return:
    """
    # 转换成时间数组
    timeArray = time.strptime(time_format, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)
    return int(timestamp)

def send_prize(detail_id, win_amount):
    """
    派奖
    # 传入detail_id 和 中奖金额
    :param detail_id:
    :param win_amount:
    :return:
    """
    ticket_no = int(str(detail_id) + str(random.randint(111110, 999990)))

    if win_amount == 0:
        bouns_status = 0
    else:
        bouns_status = 1

    lottery_url = settings.API_BASE_URL + '/notify/bonus?amount={0}&deviceId=123&ticketNo={1}&detailId={2}&bonusStatus={3}'.format(
        win_amount, ticket_no, detail_id, bouns_status)
    response = requests.get(url=lottery_url)
    response_content = json.loads(response.text)
    if response_content['code'] == '200':
        image_url = 'https://vlottery-hd1.oss-cn-hangzhou.aliyuncs.com/detail/1526548921421.jpg'
        try:
            MysqlHelper().send_prize_after(image_url=image_url,detail_id=detail_id,is_upload=1)
            return True
        except:
            return False
    else:
        return False