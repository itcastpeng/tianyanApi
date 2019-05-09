import time, random
from django.http import JsonResponse
from publicFunc import Response
from api import models
import datetime


# 判断是否给该用户发送消息
def is_send_msg(user_id):
    obj = models.Userprofile.objects.get(id=user_id)
    message_remind = int(obj.message_remind)                     # 发送消息设置
    last_message_remind_time = obj.last_message_remind_time # 最后发送消息的时间
    now = datetime.datetime.today()
    flag = False
    if message_remind == 0:
        flag = True
    else:
        if last_message_remind_time:
            flag_two = False
            if message_remind == 1:
                is_time = (now - datetime.timedelta(minutes=15))
            elif message_remind == 2:
                is_time = (now - datetime.timedelta(hours=1))
            elif message_remind == 3:
                is_time = (now - datetime.timedelta(hours=3))
            else:
                flag = False
                flag_two = True
            if not flag_two:
                if last_message_remind_time <= is_time:
                    flag = True
        else:
            flag = True
    return flag

if __name__ == '__main__':
    is_send_msg(1)