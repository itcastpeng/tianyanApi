from __future__ import absolute_import, unicode_literals
from .celery import app
from publicFunc.host import host_url
import requests, datetime
from publicFunc.qiniu_oper import update_qiniu, requests_video_download

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

@app.task
def summary_message_reminder_celery():
    url = '{}/api/summary_message_reminder_celery'.format(host_url)
    print('-----------------------------------celery---------汇总消息 发送--------> ', datetime.datetime.today(), url)
    requests.get(url)

@app.task
def update_customer_set_avator():
    url = '{}/api/update_customer_set_avator'.format(host_url)
    requests.get(url)

@app.task
def qiniu_celery_upload_video(url, video_path):
    print('-----------------------------celery--------------------下载视频=-----------> ', datetime.datetime.today())
    url = requests_video_download(url)  # 下载到本地
    update_qiniu(url, video_path)

@app.task
def celery_regularly_update_articles():
    print('-----------------------------celery--------------------更新文章=-----------> ', datetime.datetime.today())
    url = '{}/api/celery_regularly_update_articles'.format(host_url)
    requests.get(url)

















