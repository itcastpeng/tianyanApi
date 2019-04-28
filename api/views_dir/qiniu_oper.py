
from publicFunc import Response
import qiniu
from django.http import JsonResponse
from api import models
import json, requests, os
from publicFunc.qiniu_oper import qiniu_get_token,update_qiniu
from django.db.models import F


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

    #
    # elif oper_type == 'test_article':
    #     price = 0.27
    #     objs = models.Userprofile.objects.get(id=1)
    #
    #     objs.cumulative_amount = F('cumulative_amount') + price  # 累计钱数 + 30%
    #     objs.save()
    #     print('-=-----------------------000000000000000000-----------------------------------=-')
    #     objs = models.Article.objects.filter(
    #         classify__create_user__isnull=True,
    #     )
    #     for obj in objs:
    #         if 'statics' in obj.cover_img and os.path.exists(obj.cover_img):
    #             token = qiniu_get_token()
    #             img_path = update_qiniu(obj.cover_img, token)
    #             obj.cover_img = img_path
    #             obj.save()

    return JsonResponse(response.__dict__)




