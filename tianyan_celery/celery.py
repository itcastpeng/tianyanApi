from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab

app = Celery(
    broker='redis://redis_host:6379/6',
    # broker='redis://127.0.0.1:6379/0',
    backend='redis://redis_host:6379/6',
    # backend='redis://127.0.0.1:6379/0',
    include=['tianyan_celery.tasks'],

)
app.conf.enable_utc = False
app.conf.timezone = "Asia/Shanghai"
CELERYD_FORCE_EXECV = True    # 非常重要,有些情况下可以防止死锁
CELERYD_MAX_TASKS_PER_CHILD = 100    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
app.conf.beat_schedule = {

    # 天眼数据 缓存 1分钟
    'upload_day_eye':{
        'task':'tianyan_celery.tasks.upload_day_eye',
        # 'schedule': crontab("0", '*/1', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
        'schedule': crontab(minute='*/1'),  # 直接写个10为1小时执行一次  */10 为 十分钟一次
        'args':[] # # 传入任务函数的参数,可以是一个列表或元组,如果函数没参数则为空列表或空元组
    },

    # 马上超过二十四小时活跃的用户发送消息(1分钟执行一次)
    'last_active_time':{
        'task':'tianyan_celery.tasks.last_active_time',
        'schedule': crontab("*/1", '*', '*', '*', '*'),
        'args':[]
    },

    # 汇总消息 发送(1分钟执行一次)
    'summary_message_reminder_celery': {
        'task': 'tianyan_celery.tasks.summary_message_reminder_celery',
        'schedule': crontab("*/1", '*', '*', '*', '*'),
        'args': []
    },

    # 定时更新 文章 (10分钟更新一次)
    'celery_regularly_update_articles': {
        'task': 'tianyan_celery.tasks.celery_regularly_update_articles',
        'schedule': crontab("*/10", '*', '*', '*', '*'),
        'args': []
    },

}
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
