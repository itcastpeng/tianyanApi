from __future__ import absolute_import, unicode_literals
from .celery import app
from publicFunc.host import host_url
import requests

# 定时刷新 天眼谁看了我
@app.task
def upload_day_eye():
    url = '{}/api/day_eye_data?timestamp=1545822031837&rand_str=28a922b00654c407007f3d712c2fdd6b&user_id=1'.format(host_url)
    # url = 'http://127.0.0.1:8008/api/day_eye_data?timestamp=1545822031837&rand_str=28a922b00654c407007f3d712c2fdd6b&user_id=1'
    print('-----------------------------------celery---------同步天眼(谁看了我)--------> ')
    requests.get(url)










































