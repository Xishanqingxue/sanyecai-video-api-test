import requests
import time
import json
import random
import pymysql.cursors


def execute(sql, params=None, db='video_lottery'):
    # Connect to the database
    connection = pymysql.connect(host='192.168.102.91',
                                 port=3306,
                                 user='root',
                                 password='loto5522',
                                 db=db,
                                 autocommit=True,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    except:
        connection.rollback()
    finally:
        connection.close()


if __name__ == '__main__':
    while True:
        result = execute('SELECT id FROM lot_order_detail WHERE detail_status=0 and station_number is NOT NULL')
        if result:
            print('当前已派单数量:{0}'.format(len(result)))
            print('detail_ids:{0}'.format(result))

            num = 0
            detail_id_list = []
            for x in result:
                detail_id_list.append(x['id'])
            detail_id_list.sort()

            for x in detail_id_list:
                print('正在处理订单:{0}'.format(x))
                random_num = random.randint(1,101)
                if random_num < 40:
                    amount = 0
                elif 40 <= random_num < 50:
                    amount = 30
                elif 50 <= random_num < 60:
                    amount = 60
                elif 60 <= random_num < 70:
                    amount = 90
                elif 70 <= random_num < 80:
                    amount = 150
                elif 80 <= random_num < 85:
                    amount = 200
                elif 85 <= random_num < 90:
                    amount = 300
                elif 90 <= random_num < 93:
                    amount = 400
                elif 93 <= random_num < 96:
                    amount = 450
                elif 96 <= random_num < 98:
                    amount = 500
                elif 98 <= random_num < 99:
                    amount = 1000
                elif 99 <= random_num:
                    amount = 3000

                # amount = 1000

                if num == 0:
                    time.sleep(10)

                ticket_no = int(str(x) + str(random.randint(111110, 999990)))

                if amount == 0:
                    bouns_status = 0
                else:
                    bouns_status = 1

                lottery_url = 'http://192.168.102.91:8081/video-lottery-api/notify/bonus?amount={0}&deviceId=11&ticketNo={1}&detailId={2}&bonusStatus={3}'.format(amount, ticket_no, x, bouns_status)
                response = requests.get(url=lottery_url)
                response_content = json.loads(response.text)
                if response_content['code'] == '200':
                    print('订单 {0} 派奖成功'.format(x))
                    image_url = 'https://vlottery-hd1.oss-cn-hangzhou.aliyuncs.com/detail/1526548921421.jpg'
                    execute("update lot_order_detail set route=%s,is_upload=1 where id=%s",params=(image_url,x))
                    print('数据库写入图片成功')
                else:
                    print('订单 {0} 派奖失败！！！'.format(x))
                print('当前时间:{0}'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
                print('detail_id:' + str(x), '   ticket_no:' + str(ticket_no), '   amount:' + str(amount))
                print(json.loads(response.content))
                print('----------------------华丽的分割线-------------------------')
                time.sleep(5)
                num += 1
        else:
            print('没有订单!!')
        time.sleep(5)
