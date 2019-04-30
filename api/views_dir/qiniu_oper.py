
from publicFunc import Response
import qiniu
from django.http import JsonResponse
from api import models
import json, requests, os
from publicFunc.qiniu_oper import qiniu_get_token,update_qiniu
from django.db.models import F
from publicFunc.qiniu_oper import qiniu_get_token, update_qiniu, requests_img_download

# 前端请求
def qiniu_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'get_token':

        SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
        AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
        q = qiniu.Auth(AccessKey, SecretKey)
        bucket_name = 'bjhzkq_tianyan'
        token = q.upload_token(bucket_name)  # 可以指定key 图片名称

        response.code = 200
        response.msg = '生成成功'
        response.data = {'token': token}

    elif oper_type == 'test_article':
        objs = models.Userprofile.objects.all()
        for obj in objs:
            if 'http://tianyan.zhugeyingxiao.com' not in obj.qr_code:
                path = requests_img_download(obj.qr_code)
                token = qiniu_get_token()
                path = update_qiniu(path, token)
                obj.qr_code = path
                obj.save()
    return JsonResponse(response.__dict__)




