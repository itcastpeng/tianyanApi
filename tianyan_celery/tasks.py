from __future__ import absolute_import, unicode_literals
from .celery import app
from publicFunc.host import host_url
import requests, datetime

# 定时刷新 天眼谁看了我
@app.task
def upload_day_eye():
    url = '{}/api/day_eye_data?timestamp=1545822031837&rand_str=28a922b00654c407007f3d712c2fdd6b&user_id=1'.format(host_url)
    # url = 'http://127.0.0.1:8008/api/day_eye_data?timestamp=1545822031837&rand_str=28a922b00654c407007f3d712c2fdd6b&user_id=1'
    print('-----------------------------------celery---------同步天眼(谁看了我)--------> ', datetime.datetime.today())
    requests.get(url)

# 最后活跃时间马上到24小时的 发送消息
@app.task
def last_active_time():
    url = '{}/api/last_active_time?timestamp=1545822031837&rand_str=28a922b00654c407007f3d712c2fdd6b&user_id=1'.format(host_url)
    print('-----------------------------------celery---------超过24小时的发送消息--------> ', datetime.datetime.today())
    requests.get(url)

# 客户查看文章等 发送消息给用户
@app.task
def customer_view_articles_send_msg(data):
    url = '{}/api/customer_view_articles_send_msg'.format(host_url)
    print('-----------------------------------celery---------客户查看文章等 发送消息给用户--------> ', datetime.datetime.today())
    requests.post(url, data=data)

# 异步更新用户信息
@app.task
def update_user_info(ret_obj):
    url = '{}/api/update_user_info'.format(host_url)
    requests.post(url, data=ret_obj)





























