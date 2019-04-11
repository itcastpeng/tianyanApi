from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode, b64encode
import requests, datetime, random, json


# token验证 用户操作文章
def article_oper(request, oper_type):
    response = Response.ResponseObj()

    # 获取分类
    if oper_type == 'get_classify':
        now = datetime.datetime.today()
        objs = models.Classify.objects.filter(
            create_user__isnull=True,
            last_update_time__lt=now
        )
        data_list = []
        for obj in objs:
            data_list.append({
                'id': obj.id,
                'name': obj.name
            })
        response.data = data_list

    elif oper_type == '':
        pass





    return JsonResponse(response.__dict__)




