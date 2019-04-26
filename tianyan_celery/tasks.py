from __future__ import absolute_import, unicode_literals
from .celery import app
from celery_pub.eye_api import data_who_looked_at_me

import time
import datetime, requests

# 定时刷新 天眼谁看了我
@app.task
def upload_day_eye():
    data_who_looked_at_me()










































