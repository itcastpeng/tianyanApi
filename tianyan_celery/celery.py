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

    # 'schedule': crontab("*/1", '*', '*', '*', '*'),  # 此处跟 linux 中 crontab 的格式一样
    # 'schedule': crontab("5", '9, 11', '*', '*', '*'),  # 9点一次  11点一次
    # 'schedule': crontab(hour=8, minute=30),

    # 判断静态文件是否有数据 如果有上传到线上服务器
    'upload_online':{
        'task':'tianyan_celery.tasks.upload_day_eye',
        'schedule': crontab(minute=5),  # 此处跟 linux 中 crontab 的格式一样
    },







}
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
