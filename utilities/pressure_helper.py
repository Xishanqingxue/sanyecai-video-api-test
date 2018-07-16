# -*- coding:utf-8 -*-
import requests
import datetime
import time
import threading
import settings


class UrlRequest(object):

    def __init__(self):
        self.times = []
        self.error = []

    def get_resp(self, url,data):
        my_resp = UrlRequest()
        r = requests.get(url, headers=settings.API_HEADERS, data=data)

        # 获取响应时间，单位ms
        ResponseTime = float(r.elapsed.microseconds) / 1000
        # 将响应时间写入数组
        my_resp.times.append(ResponseTime)
        # 判断状态码
        if r.status_code != 200:
            my_resp.error.append("0")


class Pressure(object):
    """
    压力测试
    """

    def __init__(self,thread_number=None,think_time=0,url=None,data=None):
        self.thread_number = thread_number #并发线程数
        self.think_time = think_time #思考时间
        self.threads = []
        self.url = url
        self.data = data

    def start(self):
        url_request = UrlRequest()
        start_time = datetime.datetime.now()
        print("request start time %s" % start_time)

        for i in range(1, self.thread_number + 1):
            t = threading.Thread(target=url_request.get_resp, args=(self.url,self.data))
            self.threads.append(t)

        for t in self.threads:
            time.sleep(self.think_time)
            # 打印线程
            print("thread %s" % t)
            t.setDaemon(True)
            t.start()
        t.join()

        end_time = datetime.datetime.now()
        print("request end time %s." % end_time)

        time.sleep(3)
        # 计算数组的平均值，保留3位小数
        AverageTime = "{:.3f}".format(float(sum(url_request.times)) / float(len(url_request.times)))
        # 打印平均响应时间
        print("Average Response Time %s ms" % AverageTime)
        use_time = str(end_time - start_time)
        hour = use_time.split(':').pop(0)
        minute = use_time.split(':').pop(1)
        second = use_time.split(':').pop(2)
        # 计算总的思考时间+请求时间
        total_time = float(hour) * 60 * 60 + float(minute) * 60 + float(second)
        # 打印并发数
        print("Concurrent processing %s" % self.thread_number)
        # 打印总共消耗的时间
        print("use total time %s s" % (total_time - float(self.thread_number * self.think_time)))
        # 打印错误请求数
        print("fail request %s" % url_request.error.count("0"))